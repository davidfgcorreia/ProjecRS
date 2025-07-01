from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import file_storage
from app.models.uploaded_file import UploadedFile
from app.db import crud
from app.schemas.uploaded_file import UploadedFileCreate, UploadedFileRead

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/pdf/", response_model=UploadedFileRead)
def upload_pdf(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Save file
    filename = file_storage.save_pdf(file)
    # Create UploadedFile DB record
    uploaded_file = UploadedFile(user_id=user_id, filename=filename)
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)
    return uploaded_file
