"""Utilities to orchestrate modular processing for queries.

This module moves uploaded PDFs for a given query into a temporary
workspace and then calls the document/table extraction pipeline. The
resulting table structure is coerced into the `columns_content` format
used by the `TableData` model and persisted.

Key functions:
- move_query_pdfs_to_temp(query_id) -> str
- modular_processing_and_store(data, db) -> TableData

Notes:
- STORAGE_DIR is computed relative to this file. Caller code should ensure
    that the running user has write permissions for this directory.
"""

import os
import shutil
import re
import logging
from sqlalchemy.orm import Session
from app.models.table_data import TableData
from app.schemas.table_data import TableDataCreate
from app.processing_operation.clinical_pdf_pipeline import pipeline

logger = logging.getLogger(__name__)

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
print(f"[DEBUG] BACKEND STORAGE_DIR: {STORAGE_DIR}")
logger.debug("BACKEND STORAGE_DIR: %s", STORAGE_DIR)


def move_query_pdfs_to_temp(query_id: str) -> str:
    """Move PDFs for the given query into a temporary processing folder.

    The function looks for files in `storage/pdfs/` matching the upload
    filename convention (for example: `pdf_<user_id>_<query_id>_... .pdf`)
    and moves them into `storage/temporary/query_<query_id>/pdfs/` so the
    pipeline can operate on a workspace isolated for this query.

    Args:
        query_id: The identifier for the query whose PDFs will be processed.

    Returns:
        Absolute path to the temporary working directory for the query.
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
    try:
        entries = os.listdir(pdfs_dir)
    except Exception:
        entries = []
    logger.debug("Files in pdfs_dir: %s", entries)
    print(f"[DEBUG] Files in pdfs_dir: {entries}")
    matched = []
    # Local imports (avoid top-level circular imports in tests)
    from app.db.database import SessionLocal
    db_session = SessionLocal()
    for filename in entries:
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
    # Run the pipeline and get the real table data (headers/items)
    pipeline_result = pipeline(generatemd=False, root_storage=temp_dir, debug=True, user_id=data.userid)

    # Convert the pipeline result to columns_content for DB storage
    # columns_content should always be a list of dicts (colX: {display, meta})
    columns_content = []
    if pipeline_result and 'items' in pipeline_result:
        # Validate and coerce each row to dict of colX: {display, meta}
        for row in pipeline_result['items']:
            if isinstance(row, dict):
                columns_content.append(row)
            elif isinstance(row, list):
                # Convert list to dict with empty meta
                columns_content.append({f'col{i}': {'display': str(cell), 'meta': None} for i, cell in enumerate(row)})
            else:
                # Unexpected type, skip
                continue

    # Create a new TableData instance or update existing one
    table = db.query(TableData).filter(TableData.query_id == data.query_id).first()
    if table:
        setattr(table, 'userid', data.userid)
        setattr(table, 'num_rows', data.num_rows)
        setattr(table, 'row_ids', data.row_ids)
        setattr(table, 'columns_content', columns_content)
    else:
        table = TableData(
            query_id=data.query_id,
            userid=data.userid,
            num_rows=data.num_rows,
            row_ids=data.row_ids,
            columns_content=columns_content
        )
        db.add(table)
    db.commit()
    db.refresh(table)
    return table
