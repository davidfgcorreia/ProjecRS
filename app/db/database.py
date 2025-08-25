"""
Database configuration and utilities for ProjecRS backend.

This module sets up SQLAlchemy engines, session factories, and base model class for ORM.
It supports both SQLite (default for local/testing) and PostgreSQL (production, via DATABASE_URL env var).

Functions:
    - get_db: FastAPI dependency for DB session management.
    - hash_password: Securely hash user passwords.
    - init_admin_user: Initialize default admin user if not present.

Usage:
    Import SessionLocal and Base in models/services.
    Use get_db as a dependency in API routes.
    Set DATABASE_URL to switch between SQLite and PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import hashlib

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
SQLALCHEMY_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Use a different database for testing to avoid conflicts with the real database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test_testing.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
TestEngine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestEngine)
Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_admin_user():
    from app.models.user import User  # moved import here to avoid circular import
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(email="adm@admin.com").first()
        if not admin:
            admin = User(name="adm", email="adm@admin.com", password=hash_password("adm"), role="Adm")
            db.add(admin)
            db.commit()
    finally:
        db.close()