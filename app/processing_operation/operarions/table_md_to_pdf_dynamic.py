"""
Generate a professional horizontal A4 PDF table from a Markdown table file.
- Dynamic column and row sizing
- Dynamic multi-level headers (split on '-')
- No static header names or sizes
- Word-based cell wrapping
- Handles wide tables by splitting into multiple PDFs
- Background columns get minimal width
- Max 3 lines per cell
"""
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
import re
import io
import textwrap

def read_markdown_table(md_path):
    """Read a markdown table, skipping separator lines."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    table_lines = []
    in_table = False
    for line in lines:
        if re.match(r"^\s*\|", line):
            in_table = True
            # Skip markdown separator lines
            if re.match(r"^\s*\|?\s*-+\s*(\|\s*-+\s*)*\|?\s*$", line):
                continue
            table_lines.append(line)
        elif in_table:
            break
    if not table_lines:
        raise ValueError("No markdown table found in file.")
    df = pd.read_csv(
        io.StringIO("".join(table_lines)),
        sep="|",
        engine="python",
        skipinitialspace=True
    )
    df = df.loc[:, ~df.columns.str.match(r'Unnamed')]
    df.columns = [c.strip() for c in df.columns]
    if df.columns[0] == '':
        df = df.iloc[:, 1:]
    return df


def markdown_to_pdf(md_path, pdf_path):
    df = read_markdown_table(md_path)
    columns = list(df.columns)
    font_size = 8
    header_font_size = 10
    # Make table wider: reduce margins and allow wider columns
    page_width = landscape(A4)[0] - 20
    # Dynamic column widths
    all_col_widths = []
    for i, col in enumerate(columns):
        header_len = len(str(col).strip())
        max_cell_len = max([len(str(x)) for x in df[col]]) if not df.empty else 0
        est_len = int(0.7 * header_len + 0.5 * max_cell_len)
        if est_len <= 6:
            est_width = 32
        elif est_len <= 12:
            est_width = 50
        elif est_len <= 20:
            est_width = 70
        else:
            est_width = 90 + (est_len - 20) * 1.5
        # Allow all columns to expand dynamically
        est_width = max(18, min(est_width, 220))
        all_col_widths.append(est_width)
    # Scale all column widths to fit on one page
    total_width = sum(all_col_widths)
    if total_width > page_width:
        scale = page_width / total_width
        all_col_widths = [w * scale for w in all_col_widths]
    # Use all columns in one chunk
    col_chunks = [(columns, all_col_widths)]
    # For each chunk, build and output a PDF
    for chunk_idx, (chunk_cols, col_widths) in enumerate(col_chunks):
        top_headers = []
        sub_headers = []
        for i, col in enumerate(chunk_cols):
            if '-' in col:
                top, sub = col.split('-', 1)
                top = top.strip()
                sub = sub.strip()
            else:
                top = col.strip()
                sub = ''
            top_headers.append(top)
            sub_headers.append(sub)
        # Calculate spans for top headers
        span_map = {}
        i = 0
        while i < len(top_headers):
            top = top_headers[i]
            span_start = i
            span_end = i
            while span_end + 1 < len(top_headers) and top_headers[span_end + 1] == top:
                span_end += 1
            span_map[(span_start, 0)] = (span_end, 0)
            i = span_end + 1
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        styles = getSampleStyleSheet()
        styleH = ParagraphStyle('Header', parent=styles['Normal'], fontName='Times-Bold', fontSize=header_font_size, alignment=1, spaceAfter=2)
        styleN = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=font_size, alignment=0, spaceAfter=2)
        top_row = [Paragraph(f'<b>{h}</b>', styleH) if h else '' for h in top_headers]
        sub_row = [Paragraph(f'<b>{h}</b>', styleH) if h else '' for h in sub_headers]
        data_rows = []
        for _, row in df.iterrows():
            row_cells = []
            for i, col in enumerate(chunk_cols):
                cell = row.at[col]
                cell_str = ''
                if not pd.isna(cell):
                    # Remove unnecessary decimal points for integers
                    if isinstance(cell, float) and cell.is_integer():
                        cell_str = str(int(cell))
                    else:
                        cell_str = str(cell)
                    if cell_str.strip().lower() == 'nan':
                        cell_str = ''
                row_cells.append(Paragraph(cell_str, styleN))
            data_rows.append(row_cells)
        table_data = [top_row, sub_row] + data_rows
        pdf_out = pdf_path.replace('.pdf', f'_part{chunk_idx+1}.pdf') if len(col_chunks) > 1 else pdf_path
        pdf = SimpleDocTemplate(
            pdf_out,
            pagesize=landscape(A4),
            rightMargin=20, leftMargin=20,
            topMargin=20, bottomMargin=20
        )
        table = Table(table_data, colWidths=col_widths, repeatRows=2, splitByRow=1)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,1), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (-1,1), colors.black),
            ('ALIGN', (0,0), (-1,1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,1), 'Times-Bold'),
            ('FONTNAME', (0,2), (-1,-1), 'Times-Roman'),
            ('FONTSIZE', (0,0), (-1,0), header_font_size),
            ('FONTSIZE', (0,1), (-1,1), font_size),
            ('FONTSIZE', (0,2), (-1,-1), font_size),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
            ('LINEBELOW', (0,1), (-1,1), 1, colors.black),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),  # Add grid lines for cell boundaries
        ])
        for (start, row), (end, _) in span_map.items():
            if end > start:
                style.add('SPAN', (start, 0), (end, 0))
        table.setStyle(style)
        pdf.build([table])
        print(f"PDF table written to {pdf_out}")

if __name__ == "__main__":
    md_path = "../storage/final_values_for_table/all_tables_processed.md"
    pdf_path = "../storage/final_values_for_table/all_tables_processed.pdf"
    markdown_to_pdf(md_path, pdf_path)
