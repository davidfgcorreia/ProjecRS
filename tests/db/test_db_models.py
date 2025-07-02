import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, hash_password
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.models.query import Query
from app.models.query_file import QueryFile
from app.models.table_data import TableData

# Use in-memory SQLite for all tests
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

def test_user_create(db):
    user = User(name="Test User", email="test@example.com", password=hash_password("testpass"))
    db.add(user)
    db.commit()
    assert db.query(User).filter_by(email="test@example.com").first() is not None

def test_uploaded_file_create(db):
    user = User(name="Test User", email="test2@example.com", password=hash_password("testpass"))
    db.add(user)
    db.commit()
    file = UploadedFile(user_id=user.id, filename="file.pdf")
    db.add(file)
    db.commit()
    assert db.query(UploadedFile).filter_by(filename="file.pdf").first() is not None

def test_query_and_query_file(db):
    user = User(name="Test User", email="test3@example.com", password=hash_password("testpass"))
    db.add(user)
    db.commit()
    file = UploadedFile(user_id=user.id, filename="file2.pdf")
    db.add(file)
    db.commit()
    query = Query(user_id=user.id, report="report")
    db.add(query)
    db.commit()
    qf = QueryFile(query_id=query.id, file_id=file.id)
    db.add(qf)
    db.commit()
    assert db.query(QueryFile).filter_by(query_id=query.id, file_id=file.id).first() is not None

def test_table_data_create(db):
    # Create a TableData row and verify it can be queried
    table_data = TableData(
        query_id=1,
        userid=1,
        num_rows=2,
        row_ids=["row1", "row2"],
        columns_content=[["a", "b"], ["c", "d"]]
    )
    db.add(table_data)
    db.commit()
    result = db.query(TableData).filter_by(query_id=1).first()
    assert result is not None
    assert result.num_rows == 2
    assert result.row_ids == ["row1", "row2"]
    assert result.columns_content == [["a", "b"], ["c", "d"]]
