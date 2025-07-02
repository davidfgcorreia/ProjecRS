from sqlalchemy import Column, Integer, JSON
from app.db.database import Base

class TableData(Base):
    __tablename__ = "table_data"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, unique=True, nullable=False, index=True)
    userid = Column(Integer, nullable=False)
    num_rows = Column(Integer, nullable=False)
    row_ids = Column(JSON, nullable=False)  # List of strings
    columns_content = Column(JSON, nullable=False)  # List of list of strings