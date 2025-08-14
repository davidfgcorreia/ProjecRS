from fastapi import APIRouter, Depends, Query, Body, HTTPException # type: ignore
from sqlalchemy.orm.attributes import flag_modified #type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List
from app.db.database import get_db
from app.models.table_data import TableData
from app.schemas.table_data import TableDataRead, TableDataCreate, TableCell
from app.processing_operation.modular_processing_caller import modular_processing_and_store
from app.processing_operation.operations.merge_columns import merge_columns
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

@router.post("/update-cell/")
def update_table_cell(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Update a single cell value in the table for a given query_id, row_id, and column.
    """
    query_id = payload.get("query_id")
    row_id = payload.get("row_id")
    col = payload.get("col")
    new_value = payload.get("new_value")
    if not query_id or col is None or new_value is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found for this query_id")
    # Find the row by row_id (col0 value or index)
    row_idx = None
    for idx, row in enumerate(table.columns_content):
        if (row.get("col0") == row_id) or (str(row.get("col0")) == str(row_id)):
            row_idx = idx
            break
    if row_idx is None:
        try:
            if row_id is None:
                raise Exception()
            row_idx = int(row_id)
        except Exception:
            raise HTTPException(status_code=404, detail="Row not found.")
    # Update the cell value
    cell = table.columns_content[row_idx].get(col)
    if cell and isinstance(cell, dict):
        table.columns_content[row_idx][col]["display"] = new_value
    else:
        table.columns_content[row_idx][col] = new_value
    flag_modified(table, "columns_content")
    db.commit()
    db.refresh(table)
    return {"success": True, "query_id": query_id, "row_id": row_id, "col": col, "new_value": new_value}


@router.post("/merge-columns/", response_model=TableDataRead)
def merge_table_columns(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Merge two columns in the table for a given query_id and return the updated table.
    """
    query_id = payload.get("query_id")
    col1 = payload.get("col1")
    col2 = payload.get("col2")
    if not query_id or not col1 or not col2:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found for this query_id")
    table = merge_columns(table, col1, col2)
    flag_modified(table, "columns_content")
    flag_modified(table, "row_ids")
    flag_modified(table, "num_rows")
    db.commit()
    db.refresh(table)
    return table