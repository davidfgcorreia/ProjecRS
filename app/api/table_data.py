from fastapi import APIRouter, Depends, Query, Body, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List
from app.db.database import get_db
from app.models.table_data import TableData
from app.schemas.table_data import TableDataRead, TableDataCreate, TableCell
from app.processing_operation.modular_processing_caller import modular_processing_and_store
import asyncio
import logging

router = APIRouter(prefix="/tabledata", tags=["tabledata"])

def convert_columns_content_for_response(columns_content):
    # Ensure all cells are TableCell objects for Pydantic serialization
    if not columns_content:
        return []
    result = []
    for row in columns_content:
        row_dict = {}
        for k, v in row.items():
            if isinstance(v, TableCell):
                row_dict[k] = v
            elif isinstance(v, dict):
                row_dict[k] = TableCell(**v)
            else:
                row_dict[k] = TableCell(display=str(v), meta=None)
        result.append(row_dict)
    return result

@router.get("/", response_model=TableDataRead)
def get_table_data(
    query_id: str = Query(...),
    db: Session = Depends(get_db)
):
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found for this query_id")
    # Convert columns_content for response
    table.columns_content = convert_columns_content_for_response(table.columns_content)
    # Debug: log the response being sent
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"DEBUG API GET response: {table}")
    logging.debug(f"DEBUG API GET columns_content: {table.columns_content}")
    return table

@router.post("/filled/", response_model=TableDataRead)
async def post_filled_table(
    data: TableDataCreate = Body(...),
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    table = await loop.run_in_executor(None, modular_processing_and_store, data, db)
    # Convert columns_content for response
    table.columns_content = convert_columns_content_for_response(table.columns_content)
    # Debug: log the response being sent
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"DEBUG API POST response: {table}")
    logging.debug(f"DEBUG API POST columns_content: {table.columns_content}")
    return table