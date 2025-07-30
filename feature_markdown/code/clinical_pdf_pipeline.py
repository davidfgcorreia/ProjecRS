"""
Pipeline for processing clinical trial PDFs with manual/automatic markdown generation.
Steps:
1. Generate markdown from PDFs (optional, --generatemd)
2. Copy all tables to single markdown files
3. Manual LLM prompt step (user input)
"""
import os
import argparse
from pdf_to_markdown import batch_convert_pdfs
from copy_all_tables_to_single_md import process_all_subfolders

def pipeline(generatemd=False):
    import sys
    parser = argparse.ArgumentParser(description='Clinical PDF Pipeline')
    parser.add_argument('--root_storage', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple2')), help='Root directory for all pipeline storage')
    parser.add_argument('--generatemd', action='store_true', help='Generate markdown from PDFs')
    parser.add_argument('--md_root', help='Root directory with marker-generated markdown subfolders')
    parser.add_argument('--output_tables_root', help='Root directory to store output files')
    parser.add_argument('--debug', action='store_true', help='Use debug LLM prompt steps and outputs')
    args, _ = parser.parse_known_args(sys.argv[1:])

    DEBUG_MODE = getattr(args, 'debug', False)

    ROOT_STORAGE = args.root_storage
    pdf_dir = os.path.join(ROOT_STORAGE, 'pdfs')
    output_dir_promt1 = os.path.join(ROOT_STORAGE, 'output_file_promt_ai')
    # Create all required storage directories if not present
    storage_dirs = [
        'extracted_by_titles',
        'extracted_remain_indexes',
        'final_values_for_table',
        'final_values_for_tables',
        'markdown',
        'output_file_promt_ai',
        'parsed_index_2',
        'parsed_output_tables',
        'parsed_titles',
        'pdfs',
        'pdfs_titles',
        'table_indexs',
        'tables',
    ]
    for d in storage_dirs:
        full_path = os.path.join(ROOT_STORAGE, d)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    # Set markdown and output tables root, allowing override by CLI
    md_root = args.md_root if args.md_root else os.path.join(ROOT_STORAGE, 'markdown')
    output_tables_root = args.output_tables_root if args.output_tables_root else os.path.join(ROOT_STORAGE, 'tables')
    os.makedirs(md_root, exist_ok=True)
    os.makedirs(output_tables_root, exist_ok=True)
    # Check if md_root is empty and update generatemd accordingly
    md_files_exist = any([os.path.isfile(os.path.join(root, f)) for root, _, files in os.walk(md_root) for f in files if f.lower().endswith('.md')])
    if not md_files_exist:
        print(f"No files found in {md_root}. Setting generatemd=True.")
        generatemd = True
    # Step 1: Generate markdown from PDFs if requested
    if generatemd:
        print("[STEP 1] Generating markdown from PDFs...")
        batch_convert_pdfs(pdf_dir, md_root)  # batch_convert_pdfs processes all PDFs in the directory
        print(f"Markdown files generated in: {md_root}")
    else:
        print(f"[STEP 1] Using existing markdown files in {md_root}.")

    # Step 2: Extract tables from markdown files in all subfolders
    print("[STEP 2] Extracting tables from markdown files...")
    process_all_subfolders(md_root, output_tables_root)
    print(f"Tables extracted to: {output_tables_root}")

    if not DEBUG_MODE:

        # Step 3: Run LLM prompt on all markdown table files
        print("[STEP 3] Running LLM prompt on extracted tables...")
        from run_llm_prompt_tables import main as run_llm_prompt_tables_main
        tables_dir = os.path.join(ROOT_STORAGE, 'tables')
        indexes_path = os.path.join(ROOT_STORAGE, 'table_indexs', 'indexes.txt')
        output_file_path = os.path.join(output_dir_promt1, 'ouput_indexs.txt')
        parsed_output_tables_dir = os.path.join(ROOT_STORAGE, 'parsed_output_tables')
        #run_llm_prompt_tables_main(
        #    tables_dir=tables_dir,
        #    indexes_path=indexes_path,
        #    output_dir=output_dir_promt1,
        #    output_file=output_file_path
        #)
        print(f"LLM prompt results written to: {output_file_path}")

    else:
        print("[STEP 3] Running LLM prompt debug on tables...")
        from run_llm_degug_tables import run_chatgpt41
        tables_dir = os.path.join(ROOT_STORAGE, 'tables')
        indexes_path = os.path.join(ROOT_STORAGE, 'table_indexs', 'indexes.txt')
        output_dir_promt1_debug = os.path.join(ROOT_STORAGE, 'output_debug_file_promt_ai')
        os.makedirs(output_dir_promt1_debug, exist_ok=True)
        output_file_path = os.path.join(output_dir_promt1_debug, 'ouput_indexs.txt')
        #run_chatgpt41(
        #    tables_dir=tables_dir,
        #    indexes_path=indexes_path,
        #    output_dir=output_dir_promt1_debug,
        #    output_file=output_file_path
        #)
        print(f"LLM prompt results written to: {output_file_path}")
        output_dir_promt1 = output_dir_promt1_debug


    # Step 4: Parse output tables and save to parsed_output_tables
    print("[STEP 4] Parsing LLM output tables...")
    from parse_output_indexes import parse_and_write
    output_file_path = os.path.join(output_dir_promt1, 'ouput_indexs.txt')
    parsed_output_tables_dir = os.path.join(ROOT_STORAGE, 'parsed_output_tables')
    parse_and_write(input_file=output_file_path, output_dir=parsed_output_tables_dir)
    print(f"Parsed output tables written to: {parsed_output_tables_dir}")

    # Step 5: Extract empty indexes
    print("[STEP 5] Extracting empty indexes...")
    from extract_empty_indexes import extract_empty_indexes_all
    extracted_remain_indexes_dir = os.path.join(ROOT_STORAGE, 'extracted_remain_indexes')
    extract_empty_indexes_all(parsed_output_tables_dir, extracted_remain_indexes_dir)
    print(f"Empty indexes extraction complete. Results written to: {extracted_remain_indexes_dir}")

    # Step 6: Extract all titles from markdown files
    print("[STEP 6] Extracting all titles from markdown files...")
    from extract_titles import extract_titles_with_content
    pdfs_titles_dir = os.path.join(ROOT_STORAGE, 'pdfs_titles')
    extract_titles_with_content(md_root, pdfs_titles_dir)
    print(f"All titles extraction complete. Results written to: {pdfs_titles_dir}")

    # Step 7: Run LLM prompt on extracted titles
    print("[STEP 7] Running LLM prompt on extracted titles...")
    from run_llm_prompt_titles import main as run_llm_prompt_titles_main
    output_titles_dir = os.path.join(ROOT_STORAGE, 'output_file_tiles_promt_ai')
    os.makedirs(output_titles_dir, exist_ok=True)
    pdfs_titles_dir = os.path.join(ROOT_STORAGE, 'pdfs_titles')
    extracted_remain_indexes_dir = os.path.join(ROOT_STORAGE, 'extracted_remain_indexes')
    output_titles_file = os.path.join(output_titles_dir, 'ouput_titles.txt')
    #run_llm_prompt_titles_main(
    #    titles_dir=pdfs_titles_dir,
    #    indexes_dir=extracted_remain_indexes_dir,
    #    output_dir=output_titles_dir,
    #   output_file=output_titles_file
    #)
    print(f"LLM prompt results for titles written to: {output_titles_dir}")

    # Step 8: Parse LLM output titles and save to parsed_titles
    print("[STEP 8] Parsing LLM output titles...")
    from parse_tiles import main as parse_tiles_main
    parsed_titles_dir = os.path.join(ROOT_STORAGE, 'parsed_titles')
    os.makedirs(parsed_titles_dir, exist_ok=True)
    parse_tiles_main(
        input_file=output_titles_file,
        output_dir=parsed_titles_dir
    )

    print(f"Parsed titles written to: {parsed_titles_dir}")

    # Step 9: Copy sections by title
    print("[STEP 9] Copying sections by title...")
    from copy_sections_by_title import process_all_files as copy_sections_by_title_main
    markdown_dir = os.path.join(ROOT_STORAGE, 'markdown')
    copied_section_dir = os.path.join(ROOT_STORAGE, 'extracted_by_titles')
    all_titles_dir = os.path.join(ROOT_STORAGE, 'pdfs_titles')
    copy_sections_by_title_main(
        titles_dir=parsed_titles_dir,
        markdown_dir=markdown_dir,
        output_dir=copied_section_dir,
        all_titles_dir=all_titles_dir
    )
    print(f"Copied sections written to: {copied_section_dir}")

    if not DEBUG_MODE:

        # Step 10: Run LLM prompt on copied sections
        print("[STEP 10] Running LLM prompt on copied sections...")
        from run_llm_prompt_sections import run_chatgpt41_sections
        extracted_by_titles_dir = copied_section_dir
        extracted_remain_indexes_dir = os.path.join(ROOT_STORAGE, 'extracted_remain_indexes')
        output_sections_dir = os.path.join(ROOT_STORAGE, 'output_file_sections_promt_ai')
        os.makedirs(output_sections_dir, exist_ok=True)
        output_sections_file = os.path.join(output_sections_dir, 'ouput_sections.txt')
        #run_chatgpt41_sections(
        #    sections_dir=extracted_by_titles_dir,
        #    indexes_dir=extracted_remain_indexes_dir,
        #    output_dir=output_sections_dir,
        #    output_file=output_sections_file
        #)
        print(f"LLM prompt results for copied sections written to: {output_sections_file}")
    else:
        # Step 10: Run LLM prompt on copied sections with debug
        print("[STEP 10] Running LLM prompt debug on copied sections...")
        from run_llm_debug_sections import run_chatgpt41_sections
        extracted_by_titles_dir = copied_section_dir
        extracted_remain_indexes_dir = os.path.join(ROOT_STORAGE, 'extracted_remain_indexes')
        output_sections_dir_debug = os.path.join(ROOT_STORAGE, 'output_file_sections_debug_promt_ai')
        os.makedirs(output_sections_dir_debug, exist_ok=True)
        output_sections_file = os.path.join(output_sections_dir_debug, 'ouput_sections.txt')
        #run_chatgpt41_sections(
        #    sections_dir=extracted_by_titles_dir,
        #    indexes_dir=extracted_remain_indexes_dir,
        #    output_dir=output_sections_dir_debug,
        #    output_file=output_sections_file
        #)
        print(f"LLM prompt debug results for copied sections written to: {output_sections_file}")

    # Step 11: Parse LLM output sections and save to output_file_sections_promt_ai
    print("[STEP 11] Parsing LLM output sections...")
    from parse_index_2 import parse_and_write
    output_sections_dir_parsed = os.path.join(ROOT_STORAGE, 'parsed_index_2')
    os.makedirs(output_sections_dir_parsed, exist_ok=True)
    parse_and_write(input_file=output_sections_file, output_dir=output_sections_dir_parsed)
    print(f"Parsed sections written to: {output_sections_dir_parsed}")


    print("[STEP 12] Merging parsed outputs to final values...")
    from merge_output_indexes import main as merge_output_indexes_main
    parsed_output_tables_dir = os.path.join(ROOT_STORAGE, 'parsed_output_tables')
    parsed_index_2_dir = os.path.join(ROOT_STORAGE, 'parsed_index_2')
    final_values_dir = os.path.join(ROOT_STORAGE, 'final_values_for_tables')
    os.makedirs(final_values_dir, exist_ok=True)
    merge_output_indexes_main(parsed_output_tables_dir, parsed_index_2_dir, final_values_dir)
    print(f"Final merged values written to: {final_values_dir}")




    # Step 13: Extract and replace localizations (debug only)
    if DEBUG_MODE:
        print("[STEP 13] Extracting and replacing localizations in merged values (debug mode)...")
        from localizations import process_and_save_all
        final_values_dir = os.path.join(ROOT_STORAGE, 'final_values_for_tables')
        finalvalues_whit_ids = os.path.join(ROOT_STORAGE, 'final_values_whit_ids')
        localizations_dir = os.path.join(ROOT_STORAGE, 'localizations')
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
    from preprocess_vlaues import preprocess_directory
    preproc_output_dir = os.path.join(ROOT_STORAGE, 'preprocessed_values')
    os.makedirs(preproc_output_dir, exist_ok=True)
    preprocess_directory(preproc_input_dir, preproc_output_dir)
    print(f"Preprocessed tables written to: {preproc_output_dir}")

    # Step 15: Generate merged markdown tables
    print("[STEP 15] Generating merged markdown tables...")
    from generate_markdown_table_clean import main as generate_markdown_table_main
    final_values_for_tables_dir = preproc_output_dir
    final_values_for_table_dir = os.path.join(ROOT_STORAGE, 'final_values_for_table')
    os.makedirs(final_values_for_table_dir, exist_ok=True)
    generate_markdown_table_main(final_values_for_tables_dir, final_values_for_table_dir)
    print(f"Merged markdown tables written to: {final_values_for_table_dir}")

    # Step 16: Process merged markdown tables
    print("[STEP 16] Processing merged markdown tables...")
    from process_tables import main as process_tables_main
    final_values_for_table_dir = os.path.join(ROOT_STORAGE, 'final_values_for_table')
    process_tables_main(final_values_for_table_dir, final_values_for_table_dir)
    print(f"Processed markdown tables written to: {os.path.join(final_values_for_table_dir, 'all_tables_processed.md')}")

    # Step 17: Merge specified columns in markdown tables
    print("[STEP 17] Merging specified columns in markdown tables...")
    from merge_md_columns import merge_columns_in_md_file
    processed_md_file = os.path.join(final_values_for_table_dir, 'all_tables_processed.md')
    merged_output_file= os.path.join(final_values_for_table_dir, 'merged_columns_table.md')
    # Specify columns to merge as needed, example:
    columns_to_merge = [[7, 8], [11, 12]]
    merge_columns_in_md_file(processed_md_file, merged_output_file, columns_to_merge)
    print(f"Merged columns tables written to: {merged_output_file}")

    # Step 18: Convert processed markdown tables to .docx and .xlsx
    print("[STEP 18] Converting processed markdown tables to .docx and .xlsx...")
    from md_to_docx_xlsx import main as convert_md_dir_to_docx_xlsx
    output_docx_xlsx_dir = os.path.join(final_values_for_table_dir, 'docx_xlsx_output')
    os.makedirs(output_docx_xlsx_dir, exist_ok=True)
    convert_md_dir_to_docx_xlsx(merged_output_file, output_docx_xlsx_dir)
    print(f".docx and .xlsx files written to: {output_docx_xlsx_dir}")

if __name__ == '__main__':
    pipeline()
