from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.db.database import get_db
from app.services import file_storage
from app.models.uploaded_file import UploadedFile
from app.db import crud
from app.schemas.uploaded_file import UploadedFileCreate, UploadedFileRead
from uuid import uuid4

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/pdf/", response_model=UploadedFileRead)
def upload_pdf(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Generate a unique query_id for this upload
    query_id = uuid4().hex
    # Save file with new serialization logic
    filename = file_storage.save_pdf(file, user_id, query_id)
    # Create UploadedFile DB record
    uploaded_file = UploadedFile(user_id=user_id, filename=filename)
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)
    # Return UploadedFileRead with query_id
    return UploadedFileRead(
        id=int(uploaded_file.__dict__["id"]),
        user_id=int(uploaded_file.__dict__["user_id"]),
        filename=str(uploaded_file.__dict__["filename"]),
        upload_date=uploaded_file.__dict__["upload_date"],
        query_id=query_id
    )
