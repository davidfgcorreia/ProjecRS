"""
SQLAlchemy model for storing tabular data extracted from uploaded files and processed queries.

Fields:
    id: Primary key.
    query_id: Unique identifier for the query.
    userid: ID of the user who owns the table.
    num_rows: Number of rows in the table.
    row_ids: List of row identifiers (JSON).
    columns_content: List of row data, each as a dict of columns (JSON).
"""
from sqlalchemy import Column, Integer, JSON, String
from app.db.database import Base

class TableData(Base):
    __tablename__ = "table_data"
    id = Column(Integer, primary_key=True, index=True)  # Table row ID
    query_id = Column(String, unique=True, nullable=False, index=True)  # Query identifier
    userid = Column(Integer, nullable=False)  # User ID
    num_rows = Column(Integer, nullable=False)  # Number of rows
    row_ids = Column(JSON, nullable=False)  # List of row IDs
    columns_content = Column(JSON, nullable=False)  # List of row data (JSON)