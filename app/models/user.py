"""
SQLAlchemy model for application users (authentication, authorization, and management).

Fields:
    id: Primary key.
    name: User's name.
    email: User's email address (unique).
    password: Hashed password.
    role: User role (e.g., 'user', 'admin').
    uploaded_files: Relationship to uploaded files (one-to-many).
    queries: Relationship to queries (one-to-many).
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # User ID
    name = Column(String, index=True, nullable=False)  # Name
    email = Column(String, unique=True, index=True, nullable=False)  # Email (unique)
    password = Column(String, nullable=False)  # Hashed password
    role = Column(String, nullable=False, default="user")  # Role

    uploaded_files = relationship("UploadedFile", back_populates="user", cascade="all, delete-orphan")  # User's uploaded files
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")  # User's queries
