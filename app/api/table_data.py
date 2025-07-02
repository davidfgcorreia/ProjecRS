from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.table_data import TableData
from app.schemas.table_data import TableDataRead, TableDataCreate
from app.processing_operation.modular_processing_caller import modular_processing_and_store
import asyncio

router = APIRouter(prefix="/tabledata", tags=["tabledata"])


@router.get("/", response_model=TableDataRead)
def get_table_data(
    query_id: int = Query(...),
    db: Session = Depends(get_db)
):
    table = db.query(TableData).filter(TableData.query_id == query_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found for this query_id")
    return table


@router.post("/filled/", response_model=TableDataRead)
async def post_filled_table(
    data: TableDataCreate = Body(...),
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    table = await loop.run_in_executor(None, modular_processing_and_store, data, db)
    return table