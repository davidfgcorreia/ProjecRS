from fastapi.testclient import TestClient # type: ignore
from app.main import app
from app.db.database import get_db
from sqlalchemy.orm import Session  # type: ignore
from app.schemas.table_data import TableDataCreate

client = TestClient(app)

def override_get_db():
    # Provide a test database session here
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_post_filled_table(monkeypatch):
    # Mock the modular_processing_and_store to avoid heavy processing
    def mock_modular_processing_and_store(data, db):
        class DummyTable:
            query_id = data.query_id
            userid = data.userid
            num_rows = data.num_rows
            row_ids = data.row_ids
            columns_content = data.columns_content or [["cell_0_0"]]
        return DummyTable()

    monkeypatch.setattr(
        "app.processing_operation.modular_processing_caller.modular_processing_and_store",
        mock_modular_processing_and_store
    )

    payload = {
        "query_id": "test_query",
        "userid": 1,
        "num_rows": 1,
        "row_ids": [1],
        "columns_content": [["cell_0_0"]]
    }
    response = client.post("/tabledata/filled/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "test_query"
    assert data["userid"] == 1
    assert data["num_rows"] == 1
    assert data["row_ids"] == [1]
    assert data["columns_content"] == [["cell_0_0"]]
