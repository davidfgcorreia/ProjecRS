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
