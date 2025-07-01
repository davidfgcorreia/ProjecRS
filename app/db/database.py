from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timezone
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

upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

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

# Call this after tables are created
# init_admin_user()  # <-- Remove or comment out this call to avoid circular import during Alembic operations
