import os
import shutil
import re

from sqlalchemy.orm import Session
from app.models.table_data import TableData
from app.schemas.table_data import TableDataCreate
#from app.processing_operation.code.clinical_pdf_pipeline import pipeline

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
print(f"[DEBUG] BACKEND STORAGE_DIR: {STORAGE_DIR}")


def move_query_pdfs_to_temp(query_id):
    """
    Move all PDFs for this query to a temporary folder in storage.
    """
    pdfs_dir = os.path.join(STORAGE_DIR, 'pdfs')
    temp_dir = os.path.join(STORAGE_DIR, 'temporary', f'query_{query_id}')
    os.makedirs(temp_dir, exist_ok=True)
    temp_pdfs_dir = os.path.join(temp_dir, 'pdfs')
    os.makedirs(temp_pdfs_dir, exist_ok=True)
    # Ensure the pdfs_dir exists before listing
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir, exist_ok=True)
        return temp_dir
    # Match pattern: pdf_<user_id>_<query_id>_*.pdf
    pattern = re.compile(rf"^pdf_\d+_{query_id}_.+\.pdf$")
    print(f"[DEBUG] Files in pdfs_dir: {os.listdir(pdfs_dir)}")
    matched = []
    from app.models.uploaded_file import UploadedFile
    from app.db.database import SessionLocal
    db_session = SessionLocal()
    for filename in os.listdir(pdfs_dir):
        if pattern.match(filename):
            matched.append(filename)
            src = os.path.join(pdfs_dir, filename)
            # Parse filename: pdf_userid_dbid_queryid_filename_dbid.pdf
            # Find the part after the third underscore and before the last underscore
            try:
                first = filename.find('_', filename.find('_', filename.find('_') + 1) + 1) + 1
                last = filename.rfind('_')
                ext = os.path.splitext(filename)[1]
                if first < last:
                    original_name = filename[first:last] + ext
                else:
                    original_name = filename
            except Exception:
                original_name = filename
            dst = os.path.join(temp_pdfs_dir, original_name)
            shutil.move(src, dst)
    db_session.close()
    print(f"[DEBUG] Matched and moved: {matched}")
    return temp_dir


def modular_processing_and_store(data: TableDataCreate, db: Session):
    """
    Process and fill the columns_content of the table, then store it in the database.
    This is a placeholder for modular processing logic.
    """
    # Move PDFs for this query to a temp folder
    temp_dir = move_query_pdfs_to_temp(data.query_id)
    # Save indexes as txt file in temp_dir
    indexes_dir = os.path.join(temp_dir, 'table_indexes')
    if not os.path.exists(indexes_dir):
        os.makedirs(indexes_dir, exist_ok=True)
    indexes_path = os.path.join(indexes_dir, 'indexes.txt')
    if data.row_ids:
        with open(indexes_path, 'w', encoding='utf-8') as f:
            for idx in data.row_ids:
                f.write(f"{idx}\n")
    # Prossess columns_content and fill

    # data= pipeline(temp_dir)

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
