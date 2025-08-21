import io
import csv
from typing import Tuple
from sqlalchemy.orm import Session # type: ignore
from app.models.table_data import TableData
import os
import pandas as pd
import logging

def export_table_file(db: Session, query_id: str, file_format: str) -> Tuple[bytes, str, str]:
    logging.basicConfig(level=logging.DEBUG)
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    logging.debug(f"DEBUG export_table_file: query_id={query_id}, file_format={file_format}")
    logging.debug(f"DEBUG export_table_file: table={table}")
    if not table or not table.columns_content:
        logging.debug(f"DEBUG export_table_file: Table not found or columns_content empty for query_id={query_id}")
        raise Exception("Table not found or empty for this query_id")
    # Use column_titles if available, else fallback to row_ids or keys
    column_titles = getattr(table, 'column_titles', None)
    if column_titles and isinstance(column_titles, list):
        headers = column_titles
    elif table.row_ids and isinstance(table.row_ids, list):
        headers = table.row_ids
    else:
        first_row = table.columns_content[0]
        headers = list(first_row.keys())
    logging.debug(f"DEBUG export_table_file: headers={headers}")
    # Build rows as dicts: {header: value} for each row
    def flatten_cell(val):
        if isinstance(val, dict) and 'display' in val:
            return str(val['display'])
        elif isinstance(val, (list, tuple)):
            return ' | '.join(str(v) for v in val)
        elif isinstance(val, dict):
            return str(val)
        else:
            return str(val) if val is not None else ''
    # Flatten headers for DictWriter
    def flatten_header(header):
        if isinstance(header, (list, tuple)):
            return ' | '.join(str(h) for h in header)
        elif isinstance(header, dict):
            return str(header)
        else:
            return str(header)
    flat_headers = [flatten_header(h) for h in headers]
    flat_headers = ["File"] + flat_headers  # Add "File" as the first column header
    # Use original column names for headers
    # Filename will include 'Sistematic Revision {time}'
    from datetime import datetime
    now_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dict_rows = []
    for row in table.columns_content:
        dict_row = {}
        # Always set the first column as 'File' (col0)
        dict_row[flat_headers[0]] = flatten_cell(row.get('col0', '-')) or '-'
        # For all other columns, match flat_headers[1:] to col1, col2, ...
        for idx in range(1, len(flat_headers)):
            key = f'col{idx}'
            value = flatten_cell(row.get(key, ''))
            if value == '':
                value = '-'
            dict_row[flat_headers[idx]] = value
        dict_rows.append(dict_row)
    logging.debug(f"DEBUG export_table_file: dict_rows={dict_rows}")
    # Export based on format
    if file_format == 'csv':
        # Save CSV to the correct directory inside app/storage/temporary/query_{query_id}
        storage_dir = os.path.join(os.path.dirname(__file__), f'../storage/temporary/query_{query_id}')
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, f'Sistematic_Revision_{now_str}_{query_id}.csv')
        # Use utf-8-sig for BOM, comma delimiter, minimal quoting, and no extra whitespace
        with open(file_path, mode='w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=flat_headers, delimiter=';', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
            logging.debug(f"DEBUG CSV DictWriter: fieldnames={flat_headers}")
            writer.writeheader()
            logging.debug(f"DEBUG CSV DictWriter: wrote header {flat_headers}")
            for i, dict_row in enumerate(dict_rows):
                logging.debug(f"DEBUG CSV DictWriter: writing row {i}: {dict_row}")
                writer.writerow(dict_row)
        with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
            data = csvfile.read().encode('utf-8-sig')
            logging.debug(f"DEBUG CSV DictWriter: file content:\n{data.decode('utf-8-sig')}")
        mime = 'text/csv'
        filename = f'Sistematic_Revision_{now_str}_{query_id}.csv'
    elif file_format == 'xlsx':
        file_path = f'Sistematic_Revision_{now_str}_{query_id}.xlsx'
        import openpyxl
        from openpyxl.styles import Alignment, Font
        from openpyxl.utils import get_column_letter
        wb: 'openpyxl.Workbook' = openpyxl.Workbook()  # type: ignore
        ws: 'openpyxl.worksheet.worksheet.Worksheet' = wb.active  # type: ignore
        # Write header
        header_font = Font(bold=True)
        for col_idx, header in enumerate(flat_headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)  # type: ignore
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        # Write data rows
        for row_idx, dict_row in enumerate(dict_rows, start=2):
            for col_idx, header in enumerate(flat_headers, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=dict_row.get(header, ''))  # type: ignore
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        # Auto-fit columns
        for col_idx, header in enumerate(flat_headers, start=1):
            max_length = len(str(header))
            for row_idx in range(2, len(dict_rows) + 2):
                cell = ws.cell(row=row_idx, column=col_idx)  # type: ignore
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = max_length + 2  # type: ignore
        out_buf = io.BytesIO()
        wb.save(out_buf)
        data = out_buf.getvalue()
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = file_path
    elif file_format == 'pdf':
        # Generate a PDF using reportlab
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))
        elements = []
        style = getSampleStyleSheet()
        # Title
        elements.append(Paragraph(f"Sistematic Revision Table - Query {query_id}", style['Title']))
        elements.append(Spacer(1, 12))
        # Table data
        data_table = [flat_headers] + [ [row.get(h, '-') for h in flat_headers] for row in dict_rows ]
        t = Table(data_table)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2F3775')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(t)
        doc.build(elements)
        data = pdf_buffer.getvalue()
        mime = 'application/pdf'
        filename = f'Sistematic_Revision_{now_str}_{query_id}.pdf'
    elif file_format == 'docx':
        from docx import Document
        from docx.shared import Pt
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        doc = Document()
        table_doc = doc.add_table(rows=1, cols=len(flat_headers))
        def set_cell_border(cell):
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement('w:tcBorders')
                border_tag = OxmlElement(f'w:{border_name}')
                border_tag.set(qn('w:val'), 'single')
                border_tag.set(qn('w:sz'), '8')  # 8 eighths of a point
                border_tag.set(qn('w:space'), '0')
                border_tag.set(qn('w:color'), '000000')
                border.append(border_tag)
                tcPr.append(border)
        hdr_cells = table_doc.rows[0].cells
        for idx, header in enumerate(flat_headers):
            hdr_cells[idx].text = header
            hdr_cells[idx].paragraphs[0].runs[0].font.bold = True
            hdr_cells[idx].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Center
            set_cell_border(hdr_cells[idx])
            # Set header background color to #2F3775
            tc = hdr_cells[idx]._tc
            tcPr = tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:fill'), '2F3775')
            tcPr.append(shd)
        for dict_row in dict_rows:
            row_cells = table_doc.add_row().cells
            for idx, header in enumerate(flat_headers):
                row_cells[idx].text = dict_row.get(header, '-')
                row_cells[idx].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Center
                set_cell_border(row_cells[idx])
        out_buf = io.BytesIO()
        doc.save(out_buf)
        data = out_buf.getvalue()
        mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        filename = f'Sistematic_Revision_{now_str}_{query_id}.docx'
    else:
        logging.debug(f"DEBUG export_table_file: Unsupported format {file_format}")
        raise Exception(f"Unsupported format: {file_format}")
    logging.debug(f"DEBUG export_table_file: Exported file {filename} with mime {mime}")
    return data, mime, filename
