from pydantic import BaseModel, ConfigDict

class QueryFileBase(BaseModel):
    query_id: int
    file_id: int

class QueryFileCreate(QueryFileBase):
    pass

class QueryFileRead(QueryFileBase):
    model_config = ConfigDict(from_attributes=True)
