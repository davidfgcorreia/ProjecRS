from pydantic import BaseModel, ConfigDict, conint
from typing import List, Annotated

class TableDataBase(BaseModel):
    query_id: int
    userid: int
    num_rows: Annotated[int, conint(ge=1)]
    row_ids: List[str]
    columns_content: List[List[str]]

class TableDataCreate(TableDataBase):
    pass

class TableDataRead(TableDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)