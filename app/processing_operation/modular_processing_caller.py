import os
import shutil
import re

from sqlalchemy.orm import Session
from app.models.table_data import TableData
from app.schemas.table_data import TableDataCreate

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
print(f"[DEBUG] BACKEND STORAGE_DIR: {STORAGE_DIR}")


def move_query_pdfs_to_temp(query_id):
    """
    Move all PDFs for this query to a temporary folder in storage.
    """
    pdfs_dir = os.path.join(STORAGE_DIR, 'pdfs')
    temp_dir = os.path.join(STORAGE_DIR, 'temporary', f'query_{query_id}')
    os.makedirs(temp_dir, exist_ok=True)
    # Ensure the pdfs_dir exists before listing
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir, exist_ok=True)
        return temp_dir
    # Match pattern: pdf_<user_id>_<query_id>_*.pdf
    pattern = re.compile(rf"^pdf_\d+_{query_id}_.+\.pdf$")
    print(f"[DEBUG] Files in pdfs_dir: {os.listdir(pdfs_dir)}")
    matched = []
    for filename in os.listdir(pdfs_dir):
        if pattern.match(filename):
            matched.append(filename)
            src = os.path.join(pdfs_dir, filename)
            dst = os.path.join(temp_dir, filename)
            shutil.move(src, dst)
    print(f"[DEBUG] Matched and moved: {matched}")
    return temp_dir


def modular_processing_and_store(data: TableDataCreate, db: Session):
    """
    Process and fill the columns_content of the table, then store it in the database.
    This is a placeholder for modular processing logic.
    """
    # Move PDFs for this query to a temp folder
    move_query_pdfs_to_temp(data.query_id)
    # Always generate columns_content if not provided
    if not data.columns_content:
        filled_content = [[f"cell_{i}_{j}" for j in range(len(data.row_ids))] for i in range(data.num_rows)]
    else:
        filled_content = data.columns_content
    # Create a new TableData instance or update existing one
    table = db.query(TableData).filter(TableData.query_id == data.query_id).first()
    if table:
        setattr(table, 'userid', data.userid)
        setattr(table, 'num_rows', data.num_rows)
        setattr(table, 'row_ids', data.row_ids)
        setattr(table, 'columns_content', filled_content)
    else:
        table = TableData(
            query_id=data.query_id,
            userid=data.userid,
            num_rows=data.num_rows,
            row_ids=data.row_ids,
            columns_content=filled_content
        )
        db.add(table)
    db.commit()
    db.refresh(table)
    return table
