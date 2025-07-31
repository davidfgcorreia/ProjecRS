"""
Script to convert a markdown table (.md) to .docx and .xlsx formats.
Usage:
    python md_to_docx_xlsx.py <input_md_file> <output_dir>
Output files will be named as <table>.docx and <table>.xlsx in the output directory.
"""
import sys
import os
from pathlib import Path
import pandas as pd
from docx import Document

def parse_markdown_table(md_path):
    """Parse markdown table and return headers and rows, ignoring elements inside @@...@@."""
    import re
    # Remove all occurrences of @@...@@ (non-greedy) and trailing abbreviations like ', q.d.'
    def clean_cell(text):
        text = re.sub(r'@@.*?@@', '', text)
        # Remove trailing abbreviations (e.g., ', q.d.', ', b.i.d.', ', t.i.d.', ', q.i.d.')
        text = re.sub(r',\s*(q\.d\.|b\.i\.d\.|t\.i\.d\.|q\.i\.d\.|prn|stat|p\.o\.|i\.v\.|i\.m\.|s\.c\.|p\.r\.|p\.c\.|a\.c\.|h\.s\.|a\.m\.|p\.m\.|n\.p\.|s\.l\.|o\.d\.|o\.s\.|o\.u\.|s\.o\.|c\.c\.|gtt|mcg|IU|U|mg|ml|L|g|kg|mEq|%)\s*$', '', text, flags=re.IGNORECASE)
        return text.strip()
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip().startswith('|')]
    if not lines or len(lines) < 2:
        raise ValueError('No valid markdown table found.')
    headers = [clean_cell(h.strip()) for h in lines[0].split('|')[1:-1]]
    rows = [
        [clean_cell(cell.strip()) for cell in row.split('|')[1:-1]]
        for row in lines[2:]
    ]
    return headers, rows

def save_as_xlsx(headers, rows, out_path):
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(out_path, index=False)

def save_as_docx(headers, rows, out_path):
    from docx.shared import Inches, Pt
    from docx.enum.section import WD_ORIENT
    doc = Document()
    # Set page orientation to landscape
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(14)  # A4 landscape width
    section.page_height = Inches(8.27)
    # Set left and right margins to zero for max width
    section.left_margin = Inches(0)
    section.right_margin = Inches(0)

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # Calculate available width (page width minus margins), all as float inches
    def to_inches(val):
        # Handles Inches, Length, or None
        if val is None:
            return 0.0
        try:
            return float(val.inches)
        except AttributeError:
            return float(val)
    page_width = to_inches(section.page_width)
    left_margin = to_inches(section.left_margin)
    right_margin = to_inches(section.right_margin)
    available_width = page_width - left_margin - right_margin
    col_width_in = available_width / len(headers)
    for col in table.columns:
        for cell in col.cells:
            cell.width = Inches(col_width_in)
    # Add header with smaller font
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(7)
    # Add rows with smaller font
    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = cell_text
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(7)
    # Add note if table is too wide
    if len(headers) > 10:
        doc.add_paragraph("Note: Table columns have been shrunk to fit one page. Consider viewing in landscape mode.")
    doc.save(out_path)


def convert_md_dir_to_docx_xlsx(input_dir, output_dir):
    """
    Convert all .md files in input_dir to .docx and .xlsx in output_dir.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    md_files = list(input_dir.glob('*.md'))
    if not md_files:
        print(f'No markdown files found in {input_dir}')
        return
    for md_file in md_files:
        try:
            table_name = md_file.stem
            headers, rows = parse_markdown_table(md_file)
            xlsx_path = output_dir / f'{table_name}.xlsx'
            save_as_xlsx(headers, rows, xlsx_path)
            print(f'Excel file written to {xlsx_path}')
            docx_path = output_dir / f'{table_name}.docx'
            save_as_docx(headers, rows, docx_path)
            print(f'Docx file written to {docx_path}')
        except Exception as e:
            print(f'Error processing {md_file}: {e}')

def main(input_md=None, output_dir=None):
    if input_md is None or output_dir is None:
        if len(sys.argv) >= 3:
            input_md = sys.argv[1]
            output_dir = sys.argv[2]
        else:
            print('Usage: python md_to_docx_xlsx.py <input_md_file> <output_dir>')
            sys.exit(1)
    input_md = Path(input_md)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    table_name = input_md.stem
    headers, rows = parse_markdown_table(input_md)
    # Save as .xlsx
    xlsx_path = output_dir / f'{table_name}.xlsx'
    save_as_xlsx(headers, rows, xlsx_path)
    print(f'Excel file written to {xlsx_path}')
    # Save as .docx
    docx_path = output_dir / f'{table_name}.docx'
    save_as_docx(headers, rows, docx_path)
    print(f'Docx file written to {docx_path}')

if __name__ == '__main__':
    main()
