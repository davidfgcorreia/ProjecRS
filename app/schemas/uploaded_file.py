from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UploadedFileBase(BaseModel):
    filename: str
    upload_date: datetime

class UploadedFileCreate(BaseModel):
    user_id: int
    filename: str

class UploadedFileRead(UploadedFileBase):
    id: int
    user_id: int
    query_id: str
    model_config = ConfigDict(from_attributes=True)
