"""Schemas for uploaded query files.

This module defines Pydantic models used to validate and serialize information
about uploaded files (for example, PDFs or other documents uploaded by users).

Models:
- QueryFileBase / QueryFileCreate / QueryFileRead: internal shapes used by endpoints.
- QueryFile: minimal metadata about an uploaded file (filename, content_type, size).
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class QueryFileBase(BaseModel):
    query_id: int
    file_id: int


class QueryFileCreate(QueryFileBase):
    pass


class QueryFile(BaseModel):
    """Metadata for an uploaded file.

    Attributes:
        filename: The original filename uploaded by the user.
        content_type: Optional MIME content type detected for the file.
        size: Optional file size in bytes.
    """
    filename: str
    content_type: Optional[str] = None
    size: Optional[int] = None


class QueryFileRead(QueryFileBase):
    model_config = ConfigDict(from_attributes=True)
