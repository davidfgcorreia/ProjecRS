import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import crud
from app.models.user import User
from app.schemas.user import UserCreate
from app.db.database import Base

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Type hint for better editor support
def get_id(obj: User) -> int:
    return obj.id # type: ignore

def test_create_and_get_user(db):
    user = UserCreate(name="Test", email="test@x.com", password="pw")
    db_user = crud.create_user(db, user)  
    assert db_user.email == user.email   # type: ignore
    fetched = crud.get_user(db, get_id(db_user))  
    assert fetched is not None
    assert fetched.email == user.email  # type: ignore

def test_get_user_by_email(db):
    user = UserCreate(name="Test2", email="test2@x.com", password="pw")
    crud.create_user(db, user)  # type: ignore
    fetched = crud.get_user_by_email(db, user.email)  
    assert fetched is not None
    assert fetched.email == user.email # type: ignore

def test_get_users(db):
    for i in range(3):
        crud.create_user(db, UserCreate(name=f"U{i}", email=f"u{i}@x.com", password="pw"))  
    users = crud.get_users(db)  # type: ignore
    assert len(users) >= 3

def test_update_user(db):
    user = UserCreate(name="Old", email="old@x.com", password="pw")
    db_user = crud.create_user(db, user) 
    updated = crud.update_user(db, get_id(db_user), UserCreate(name="New", email="new@x.com", password="pw"))  # type: ignore
    assert updated is not None
    assert updated.name == "New" # type: ignore
    assert updated.email == "new@x.com" # type: ignore

def test_delete_user(db):
    user = UserCreate(name="Del", email="del@x.com", password="pw")
    db_user = crud.create_user(db, user) 
    crud.delete_user(db, get_id(db_user)) 
    assert crud.get_user(db, get_id(db_user)) is None 
