from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from datetime import datetime, timezone
from app.db.database import Base

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    report = Column(Text)

    user = relationship("User", back_populates="queries")
    query_files = relationship("QueryFile", back_populates="query")


