"""Schemas for uploaded file metadata.

Simple Pydantic models used to represent file upload metadata in API
requests and responses.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UploadedFileBase(BaseModel):
    """Base fields describing an uploaded file."""
    filename: str
    upload_date: datetime


class UploadedFileCreate(BaseModel):
    """Payload used when creating a new uploaded file record."""
    user_id: int
    filename: str


class UploadedFileRead(UploadedFileBase):
    """Representation returned by the API when reading an uploaded file."""
    id: int
    user_id: int
    query_id: str
    model_config = ConfigDict(from_attributes=True)
