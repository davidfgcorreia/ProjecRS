"""Schemas for query-related API payloads.

This module defines Pydantic models used for creating and returning query
records. These schemas are used by the API routers to validate incoming data
and to serialize responses.

Models:
- Query: basic representation of a query entity exposed via the API.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class QueryBase(BaseModel):
    query_date: datetime
    report: Optional[str] = None

class QueryCreate(BaseModel):
    user_id: int
    report: Optional[str] = None

class QueryRead(QueryBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
