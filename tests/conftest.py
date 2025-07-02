import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db

# Explicitly import all model modules to ensure table registration
import app.models.user
import app.models.uploaded_file
import app.models.query
import app.models.query_file
import app.models.table_data

# Use a single in-memory SQLite connection for all tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=connection)
    yield
    Base.metadata.drop_all(bind=connection)
    connection.close()

# Dependency override for FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

import app.main
app.main.app.dependency_overrides[get_db] = override_get_db
