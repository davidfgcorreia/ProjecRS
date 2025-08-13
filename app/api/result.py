from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.db.database import get_db
from app.models.query import Query
from app.models.query_file import QueryFile
from app.models.uploaded_file import UploadedFile
from app.services import file_storage
from app.schemas.query import QueryRead
from app.schemas.uploaded_file import UploadedFileRead

router = APIRouter(prefix="/result", tags=["result"])

@router.get("/{query_id}", response_model=QueryRead)
def get_result_table(query_id: int, db: Session = Depends(get_db)):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query

@router.get("/report/{query_id}")
def get_report(query_id: int, db: Session = Depends(get_db)):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"report": query.report}

@router.get("/table-info/{query_id}", response_model=dict)
def get_table_info(query_id: int, db: Session = Depends(get_db)):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    file_links = db.query(QueryFile).filter(QueryFile.query_id == query_id).all()
    files = [db.query(UploadedFile).filter(UploadedFile.id == qf.file_id).first() for qf in file_links]
    return {
        "files": [UploadedFileRead.from_orm(f) for f in files if f],
        "columns": []
    }
