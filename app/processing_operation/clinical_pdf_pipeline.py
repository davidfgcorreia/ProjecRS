"""
Pipeline for processing clinical trial PDFs with manual/automatic markdown generation.
Steps:
1. Generate markdown from PDFs (optional, --generatemd)
2. Copy all tables to single markdown files
3. Manual LLM prompt step (user input)
"""
import os
import argparse
from app.processing_operation.operarions.pdf_to_markdown import batch_convert_pdfs

def pipeline(generatemd=False, root_storage=None , debug=False):


    if root_storage is None:
        raise ValueError("root_storage must not be None")
    pdf_dir = os.path.join(root_storage, 'pdfs')


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
        full_path = os.path.join(root_storage, d)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    # Set markdown and output tables root, allowing override by function arguments
    md_root = os.path.join(root_storage, 'markdown')
    os.makedirs(md_root, exist_ok=True)
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


if __name__ == '__main__':
    pipeline()
