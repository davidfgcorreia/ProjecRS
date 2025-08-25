
"""Clinical PDF processing pipeline.

This module implements a multi-step pipeline used to convert uploaded PDF
papers into cleaned, merged markdown tables suitable for downstream
annotation and LLM prompting. The pipeline is intentionally modular — each
step writes intermediate artifacts into the provided `root_storage` workspace
so the process can be debugged or re-run from an intermediate stage.

Main functionality
------------------
- copy_query_to_markdowns(temp_query_dir, markdowns_root, user_id, paper_title)
    Copies a temporary markdown workspace into the persistent `markdowns/`
    directory under a user-scoped folder (markdowns/{user_id}/{paper_title}).

- pipeline(generatemd=False, root_storage=None, debug=False, user_id=None)
    Orchestrates the full processing flow for a single query workspace. It
    optionally converts PDFs to markdown, extracts tables, runs LLM prompts
    (or debug variants), parses outputs, merges and postprocesses results,
    and finally returns a compact representation of merged headers and
    items suitable for the application's `TableData` storage format.

Inputs and outputs
------------------
- root_storage (str): Path to a temporary workspace for this query. The
    pipeline creates and reads subfolders beneath this root (pdfs, markdown,
    tables, etc.). Must be provided and writable by the process user.
- user_id (int): Numeric id of the user that owns the query. Used when
    copying results into the persistent `markdowns/` area.
- Returns: When successful the pipeline returns a dict with keys
    `headers` (list) and `items` (list of rows). If the merged markdown
    artifact is not present the function returns None.

Notes and behavior
------------------
- Many intermediate files and directories are created under the provided
    `root_storage` path; this makes debugging straightforward but requires
    sufficient disk space.
- The pipeline expects the `operarions` helpers to exist and to follow the
    interface used below (for example `batch_convert_pdfs`, `process_all_subfolders`,
    etc.). Errors in those modules will propagate and should be handled by
    the caller if needed.

Example usage::

        result = pipeline(generatemd=True, root_storage='/tmp/query123', debug=False, user_id=42)
        if result:
                headers, items = result['headers'], result['items']

"""

from __future__ import annotations

import os
import json
import shutil
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

from app.processing_operation.operarions.pdf_to_markdown import batch_convert_pdfs
from app.processing_operation.operarions.copy_all_tables_to_single_md import process_all_subfolders
from app.processing_operation.operarions.run_llm_prompt_tables import main as run_llm_prompt_tables_main
from app.processing_operation.operarions.run_llm_degug_tables import run_chatgpt41
from app.processing_operation.operarions.parse_output_indexes import parse_and_write
from app.processing_operation.operarions.extract_empty_indexes import extract_empty_indexes_all
from app.processing_operation.operarions.extract_titles import extract_titles_with_content
from app.processing_operation.operarions.run_llm_prompt_titles import main as run_llm_prompt_titles_main
from app.processing_operation.operarions.parse_tiles import main as parse_tiles_main
from app.processing_operation.operarions.copy_sections_by_title import process_all_files as copy_sections_by_title_main
from app.processing_operation.operarions.run_llm_prompt_sections import run_chatgpt41_sections
from app.processing_operation.operarions.run_llm_debug_sections import run_chatgpt41_sections
from app.processing_operation.operarions.parse_index_2 import parse_and_write
from app.processing_operation.operarions.merge_output_indexes import main as merge_output_indexes_main
from app.processing_operation.operarions.localizations import process_and_save_all
from app.processing_operation.operarions.preprocess_vlaues import preprocess_directory
from app.processing_operation.operarions.generate_markdown_table_clean import main as generate_markdown_table_main
from app.processing_operation.operarions.md_table_to_js import parse_md_table
from app.processing_operation.operarions.process_tables import main as process_markdown


def copy_query_to_markdowns(temp_query_dir: str, markdowns_root: str, user_id: int, paper_title: str) -> None:
    """Copy a temporary markdown workspace into the persistent markdowns area.

    The function preserves the directory structure for the paper under
    `markdowns/{user_id}/{paper_title}`. Existing destination folders are
    removed before copying to ensure a clean overwrite.

    Args:
        temp_query_dir: Path to the temporary markdown directory to copy.
        markdowns_root: Root path where user markdowns are stored.
        user_id: Numeric id of the user (used to create the owner directory).
        paper_title: Title (used as the directory name) of the paper being copied.
    """
    dest_dir = os.path.join(markdowns_root, str(user_id), paper_title)
    os.makedirs(dest_dir, exist_ok=True)

    for item in os.listdir(temp_query_dir):
        src_path = os.path.join(temp_query_dir, item)
        dest_path = os.path.join(dest_dir, item)
        if os.path.isdir(src_path):
            # Recursively copy the entire directory
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)
    logger.info("Copied all contents from %s to %s", temp_query_dir, dest_dir)
    print(f"Copied all contents from {temp_query_dir} to {dest_dir}")

def pipeline(generatemd: bool = False, root_storage: Optional[str] = None, debug: bool = False, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Orchestrate the end-to-end clinical PDF -> merged markdown pipeline.

    Args:
        generatemd: If True, convert PDFs to markdown even if existing
            markdown files are not present.
        root_storage: Path to the temporary workspace created for this
            query. The function will read/write subdirectories under this
            path (pdfs, markdown, tables, etc.). Must be provided.
        debug: When True, runs debug variants of LLM prompts and writes
            outputs to debug-named directories to avoid overwriting normal
            outputs.
        user_id: Numeric id of the user owning the query. Required so the
            pipeline can copy artifacts to the persistent `markdowns/`
            directory for the user.

    Returns:
        A dict with keys `headers` and `items` representing the merged
        markdown table content, or None if the merged artifact is absent.
    """

    if root_storage is None:
        raise ValueError("root_storage must not be None")
    pdf_dir = os.path.join(root_storage, 'pdfs')

    if user_id is None:
        raise ValueError("user_id must not be None for processing PDFs")


    # Set markdown and output tables root, allowing override by function arguments
    md_root = os.path.join(root_storage, 'markdown')
    os.makedirs(md_root, exist_ok=True)
    # Ensure markdowns_root always points to the main markdowns directory (app/storage/markdowns)
    # Main markdowns directory (two levels up from temp root_storage)
    markdowns_root = os.path.abspath(os.path.join(root_storage, '..', '..', 'markdowns'))
    md_files_exist = False
    # For each PDF, check if a markdown for this paper is already present in the user's markdowns directory
    for fname in os.listdir(pdf_dir):
        if fname.lower().endswith('.pdf'):
            paper_title = os.path.splitext(fname)[0]
            user_paper_dir = os.path.join(markdowns_root, str(user_id), paper_title)
            dest_paper_dir = os.path.join(md_root, paper_title)
            if os.path.exists(user_paper_dir):
                # Copy only the folder corresponding to the paper title
                if os.path.exists(dest_paper_dir):
                    shutil.rmtree(dest_paper_dir)
                shutil.copytree(user_paper_dir, dest_paper_dir)
                print(f"Copied existing markdown folder for {paper_title} from user markdowns to temp.")
                md_files_exist = True
    # If no markdowns were found/copied, set generatemd True
    if not md_files_exist:
        print(f"No files found in {md_root}. Setting generatemd=True.")
        generatemd = True
    # Step 1: Generate markdown from PDFs if requested
    if generatemd:
        print("[STEP 1] Generating markdown from PDFs...")
        # Only process PDFs that do not already have markdowns copied
        needed_pdfs = []
        for fname in os.listdir(pdf_dir):
            if fname.lower().endswith('.pdf'):
                paper_title = os.path.splitext(fname)[0]
                dest_paper_dir = os.path.join(md_root, paper_title)
                if not os.path.exists(dest_paper_dir):
                    needed_pdfs.append(fname)
        if needed_pdfs:
            batch_convert_pdfs(pdf_dir, md_root, needed_pdfs)  # Only process needed PDFs
            print(f"Markdown files generated in: {md_root}")
            # After generating markdown, copy to markdowns/{user_id}/{paper_title}
            for fname in needed_pdfs:
                paper_title = os.path.splitext(fname)[0]
                temp_query_dir = os.path.join(md_root, paper_title)
                copy_query_to_markdowns(temp_query_dir, markdowns_root, user_id, paper_title)
        else:
            print("No new PDFs to process.")
    else:
        print(f"[STEP 1] Using existing markdown files in {md_root}.")

     # Step 2: Extract tables from markdown files in all subfolders
    output_tables_root =  os.path.join(root_storage, 'tables')
    os.makedirs(output_tables_root, exist_ok=True)
    print("[STEP 2] Extracting tables from markdown files...")
    process_all_subfolders(md_root, output_tables_root)
    print(f"Tables extracted to: {output_tables_root}")

    if not debug:
        # Step 3: Run LLM prompt on all markdown table files
        print("[STEP 3] Running LLM prompt on extracted tables...")
        indexes_path = os.path.join(root_storage, 'table_indexes', 'indexes.txt')
        os.makedirs(os.path.dirname(indexes_path), exist_ok=True)
        output_dir_promt1 = os.path.join(root_storage, 'output_file_promt1')
        os.makedirs(output_dir_promt1, exist_ok=True)
        output_file_path = os.path.join(output_dir_promt1, 'ouput_indexs.txt')
        run_llm_prompt_tables_main(
            tables_dir=output_tables_root,
            indexes_path=indexes_path,
            output_dir=output_dir_promt1,
            output_file=output_file_path
        )
        print(f"LLM prompt results written to: {output_file_path}")
    else:
        # Step 3: Run LLM prompt debug on all markdown table files
        print("[STEP 3] Running LLM prompt debug on tables...")
        indexes_path = os.path.join(root_storage, 'table_indexes', 'indexes.txt')
        # Ensure the indexes.txt file exists (create empty if missing)

        if not indexes_path:
            raise FileNotFoundError("Indexes file not found")
        output_dir_promt1 = os.path.join(root_storage, 'output_debug_file_promt_ai')
        os.makedirs(output_dir_promt1, exist_ok=True)
        output_file_path = os.path.join(output_dir_promt1, 'ouput_indexs.txt')
        run_chatgpt41(
            tables_dir=output_tables_root,
            indexes_path=indexes_path,
            output_dir=output_dir_promt1,
            output_file=output_file_path
        )
        print(f"LLM prompt results written to: {output_file_path}")

    # Step 4: Parse output tables and save to parsed_output_tables
    print("[STEP 4] Parsing LLM output tables...")
    output_file_path = os.path.join(output_dir_promt1, 'ouput_indexs.txt')
    parsed_output_tables_dir = os.path.join(root_storage, 'parsed_output_tables')
    parse_and_write(input_file=output_file_path, output_dir=parsed_output_tables_dir)
    print(f"Parsed output tables written to: {parsed_output_tables_dir}")

    # Step 5: Extract empty indexes
    print("[STEP 5] Extracting empty indexes...")
    extracted_remain_indexes_dir = os.path.join(root_storage, 'extracted_remain_indexes')
    extract_empty_indexes_all(parsed_output_tables_dir, extracted_remain_indexes_dir)
    print(f"Empty indexes extraction complete. Results written to: {extracted_remain_indexes_dir}")

    # Step 6: Extract all titles from markdown files
    print("[STEP 6] Extracting all titles from markdown files...")
    pdfs_titles_dir = os.path.join(root_storage, 'pdfs_titles')
    extract_titles_with_content(md_root, pdfs_titles_dir)
    print(f"All titles extraction complete. Results written to: {pdfs_titles_dir}")


     # Step 7: Run LLM prompt on extracted titles
    print("[STEP 7] Running LLM prompt on extracted titles...")
    output_titles_dir = os.path.join(root_storage, 'output_file_tiles_promt_ai')
    os.makedirs(output_titles_dir, exist_ok=True)
    pdfs_titles_dir = os.path.join(root_storage, 'pdfs_titles')
    extracted_remain_indexes_dir = os.path.join(root_storage, 'extracted_remain_indexes')
    output_titles_file = os.path.join(output_titles_dir, 'ouput_titles.txt')
    run_llm_prompt_titles_main(
        titles_dir=pdfs_titles_dir,
        indexes_dir=extracted_remain_indexes_dir,
        output_dir=output_titles_dir,
       output_file=output_titles_file
    )
    print(f"LLM prompt results for titles written to: {output_titles_dir}")

     # Step 8: Parse LLM output titles and save to parsed_titles
    print("[STEP 8] Parsing LLM output titles...")
    parsed_titles_dir = os.path.join(root_storage, 'parsed_titles')
    os.makedirs(parsed_titles_dir, exist_ok=True)
    parse_tiles_main(
        input_file=output_titles_file,
        output_dir=parsed_titles_dir
    )

    print(f"Parsed titles written to: {parsed_titles_dir}")

    # Step 9: Copy sections by title
    print("[STEP 9] Copying sections by title...")
    copied_section_dir = os.path.join(root_storage, 'extracted_by_titles')
    copy_sections_by_title_main(
        titles_dir=parsed_titles_dir,
        markdown_dir=md_root,
        output_dir=copied_section_dir,
        all_titles_dir=pdfs_titles_dir
    )
    print(f"Copied sections written to: {copied_section_dir}")

    if not debug:

        # Step 10: Run LLM prompt on copied sections
        print("[STEP 10] Running LLM prompt on copied sections...")
        output_sections_dir = os.path.join(root_storage, 'output_file_sections_promt_ai')
        os.makedirs(output_sections_dir, exist_ok=True)
        output_sections_file = os.path.join(output_sections_dir, 'ouput_sections.txt')
        run_chatgpt41_sections(
            sections_dir=copied_section_dir,
            indexes_dir=extracted_remain_indexes_dir,
            output_dir=output_sections_dir,
            output_file=output_sections_file
        )
        print(f"LLM prompt results for copied sections written to: {output_sections_file}")
    else:
        # Step 10: Run LLM prompt on copied sections with debug
        print("[STEP 10] Running LLM prompt debug on copied sections...")
        output_sections_dir_debug = os.path.join(root_storage, 'output_file_sections_debug_promt_ai')
        os.makedirs(output_sections_dir_debug, exist_ok=True)
        output_sections_file = os.path.join(output_sections_dir_debug, 'ouput_sections.txt')
        run_chatgpt41_sections(
            sections_dir=copied_section_dir,
            indexes_dir=extracted_remain_indexes_dir,
            output_dir=output_sections_dir_debug,
            output_file=output_sections_file
        )
        print(f"LLM prompt debug results for copied sections written to: {output_sections_file}")

    # Step 11: Parse LLM output sections and save to output_file_sections_promt_ai
    print("[STEP 11] Parsing LLM output sections...")
    output_sections_dir_parsed = os.path.join(root_storage, 'parsed_index_2')
    os.makedirs(output_sections_dir_parsed, exist_ok=True)
    parse_and_write(input_file=output_sections_file, output_dir=output_sections_dir_parsed)
    print(f"Parsed sections written to: {output_sections_dir_parsed}")


    print("[STEP 12] Merging parsed outputs to final values...")
    final_values_dir = os.path.join(root_storage, 'final_values_for_tables')
    os.makedirs(final_values_dir, exist_ok=True)
    merge_output_indexes_main(parsed_output_tables_dir, output_sections_dir_parsed, final_values_dir)
    print(f"Final merged values written to: {final_values_dir}")

        # Step 13: Extract and replace localizations (debug only)
    if debug:
        print("[STEP 13] Extracting and replacing localizations in merged values (debug mode)...")
        finalvalues_whit_ids = os.path.join(root_storage, 'final_values_whit_ids')
        localizations_dir = os.path.join(root_storage, 'localizations')
        os.makedirs(localizations_dir, exist_ok=True)
        os.makedirs(finalvalues_whit_ids, exist_ok=True)
        loc_json_path = os.path.join(localizations_dir, 'localizations_map.json')
        process_and_save_all(final_values_dir, localizations_dir, loc_json_path)
        print(f"Localizations extracted and cleaned files written to: {localizations_dir}")
        preproc_input_dir = localizations_dir
    else:
        preproc_input_dir = final_values_dir
    # Step 14: Preprocess merged values (remove branch if all values are the same)
    print("[STEP 14] Preprocessing merged values (removing branch notation if all values are the same)...")
    preproc_output_dir = os.path.join(root_storage, 'preprocessed_values')
    os.makedirs(preproc_output_dir, exist_ok=True)
    preprocess_directory(preproc_input_dir, preproc_output_dir)
    print(f"Preprocessed tables written to: {preproc_output_dir}")

    # Step 15: Generate merged markdown tables
    print("[STEP 15] Generating merged markdown tables...")
    final_values_for_tables_dir = preproc_output_dir
    final_values_for_table_dir = os.path.join(root_storage, 'final_values_for_table')
    os.makedirs(final_values_for_table_dir, exist_ok=True)
    generate_markdown_table_main(final_values_for_tables_dir, final_values_for_table_dir)
    print(f"Merged markdown tables written to: {final_values_for_table_dir}")

    # Step 16 : Postprocess values
    print ("[STEP 16] Postprocessing values...")
    postprocess_directory = os.path.join(root_storage, 'postprocessed_values')
    os.makedirs(postprocess_directory, exist_ok=True)
    process_markdown(final_values_for_table_dir, postprocess_directory)
    print(f"Postprocessed tables written to: {postprocess_directory}")

    # Parse the merged markdown table and return real headers/items
    merged_md_path = os.path.join(postprocess_directory, 'all_tables_processed.md')
    if os.path.exists(merged_md_path):
        headers, items = parse_md_table(merged_md_path)
        print("[PIPELINE OUTPUT] headers:")
        print(json.dumps(headers, indent=2))
        print("[PIPELINE OUTPUT] items:")
        print(json.dumps(items, indent=2))
        return {'headers': headers, 'items': items}
    else:
        print(f"[WARNING] Merged markdown table not found at {merged_md_path}")
        return None

if __name__ == '__main__':
    result = pipeline()
    if result:
        print(json.dumps(result, indent=2))
