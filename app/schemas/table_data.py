from pydantic import BaseModel, ConfigDict, conint
from typing import List, Annotated, Optional

class TableDataBase(BaseModel):
    query_id: str  # changed from int to str
    userid: int
    num_rows: Annotated[int, conint(ge=1)]
    row_ids: List[str]
    columns_content: Optional[List[List[str]]] = None

class TableDataCreate(TableDataBase):
    pass

class TableDataRead(TableDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)