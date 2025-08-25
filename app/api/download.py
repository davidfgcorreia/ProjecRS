"""
Download API endpoints for exporting and downloading files in various formats.

Defines routes for downloading table data as CSV, XLSX, PDF, DOCX, etc.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session 
from app.db.database import get_db
from app.models.table_data import TableData
from app.services.table_export import export_table_file
import logging

router = APIRouter()

@router.get("/download/")
def download_table_file(
    format: str = Query(..., regex="^(csv|xlsx|pdf|docx)$"),
    query_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Download the processed table file in the requested format for a given query_id.
    """
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"DEBUG download API: query_id={query_id}, format={format}")
    # Check all query_ids in the database for diagnostics
    all_ids = [row.query_id for row in db.query(TableData).all()]
    logging.debug(f"DEBUG download API: all query_ids in DB: {all_ids}")
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    logging.debug(f"DEBUG download API: table={table}")
    if not table:
        logging.debug(f"DEBUG download API: Table not found for query_id={query_id}. All IDs: {all_ids}")
        raise HTTPException(status_code=404, detail=f"Table not found for this query_id. All IDs: {all_ids}")
    if not getattr(table, "columns_content", None):
        logging.debug(f"DEBUG download API: columns_content is empty for query_id={query_id}")
        raise HTTPException(status_code=404, detail=f"Table columns_content is empty for query_id={query_id}")
    try:
        file_bytes, mime_type, filename = export_table_file(db, query_id, format)
    except Exception as e:
        logging.debug(f"DEBUG download API: export_table_file error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"File not found or error: {str(e)}")
    return Response(content=file_bytes, media_type=mime_type, headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
