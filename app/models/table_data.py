from sqlalchemy import Column, Integer, JSON, String  # type: ignore
from app.db.database import Base

class TableData(Base):
    __tablename__ = "table_data"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String, unique=True, nullable=False, index=True)
    userid = Column(Integer, nullable=False)
    num_rows = Column(Integer, nullable=False)
    row_ids = Column(JSON, nullable=False)
    # Now stores a list of dicts (each row: {col0: {display, meta}, ...})
    columns_content = Column(JSON, nullable=False)