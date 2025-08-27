"""Schemas describing table data exchanged with the API.

This module contains Pydantic models that mirror the `TableData` database
model and validate table content sent between the frontend and backend.
"""

from pydantic import BaseModel, ConfigDict, conint, Field # type: ignore
from typing import List, Annotated, Optional, Dict, Any


class TableCell(BaseModel):
    """Represents a single table cell's display value and optional metadata.

    Attributes:
        display: The rendered display value for the cell (string).
        meta: Optional string with additional metadata about the cell.
    """
    display: str
    meta: Optional[str] = None


class TableDataBase(BaseModel):
    """Base schema for table data operations.

    Attributes:
        query_id: The identifier of the associated query.
        userid: Numeric user id who owns the table.
        num_rows: Number of rows in the table (must be >= 1).
        row_ids: List of row identifier strings.
        columns_content: Optional list of per-row dicts mapping column keys
                         (e.g., 'col0') to TableCell objects.
    """
    query_id: str
    userid: int
    num_rows: Annotated[int, conint(ge=1)]
    row_ids: List[str]
    # List of dicts, each dict: {col0: {display, meta}, ...}
    columns_content: Optional[List[Dict[str, TableCell]]] = Field(default=None, description="List of table rows, each as dict of colX: TableCell")
    # Pydantic v2: use model_config instead of class Config
    # The previous json_encoders that converted TableCell to dict are not required
    # because TableCell is a BaseModel and will serialize correctly in v2.
    model_config = ConfigDict(arbitrary_types_allowed=True)


class TableDataCreate(TableDataBase):
    """Schema used for creating a new table record."""
    pass


class TableDataRead(TableDataBase):
    """Schema used to return a stored table record with its id."""
    id: int
    model_config = ConfigDict(from_attributes=True)