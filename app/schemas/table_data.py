from pydantic import BaseModel, ConfigDict, conint, Field # type: ignore
from typing import List, Annotated, Optional, Dict, Any

class TableCell(BaseModel):
    display: str
    meta: Optional[str] = None

class TableDataBase(BaseModel):
    query_id: str
    userid: int
    num_rows: Annotated[int, conint(ge=1)]
    row_ids: List[str]
    # List of dicts, each dict: {col0: {display, meta}, ...}
    columns_content: Optional[List[Dict[str, TableCell]]] = Field(default=None, description="List of table rows, each as dict of colX: TableCell")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            TableCell: lambda v: v.dict() if isinstance(v, TableCell) else v
        }

class TableDataCreate(TableDataBase):
    pass

class TableDataRead(TableDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)