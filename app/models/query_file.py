from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class QueryFile(Base):
    __tablename__ = "query_files"
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), primary_key=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), primary_key=True)

    query = relationship("Query", back_populates="query_files")
    file = relationship("UploadedFile", back_populates="query_files")
