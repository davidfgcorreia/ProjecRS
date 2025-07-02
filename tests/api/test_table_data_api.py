import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def create_user():
    email = f"tableuser_{uuid.uuid4().hex}@example.com"
    resp = client.post("/users/", json={"name": "TableUser", "email": email, "password": "testpass"})
    assert resp.status_code == 200
    return resp.json()["id"]

def get_test_db():
    # Use the same session as the FastAPI dependency override
    for dep in app.dependency_overrides.values():
        return next(dep())
    raise RuntimeError("No test DB session found")

def create_query(user_id):
    from app.models.query import Query
    db = get_test_db()
    query = Query(user_id=user_id, report="test report")
    db.add(query)
    db.commit()
    db.refresh(query)
    db.close()
    return query.id

def test_post_and_get_table_data():
    user_id = create_user()
    query_id = create_query(user_id)
    data = {
        "query_id": query_id,
        "userid": user_id,
        "num_rows": 2,
        "row_ids": ["row1", "row2"],
        "columns_content": [["a", "b"], ["c", "d"]]
    }
    resp = client.post("/tabledata/filled/", json=data)
    assert resp.status_code == 200
    returned = resp.json()
    assert returned["query_id"] == query_id
    assert returned["userid"] == user_id
    assert returned["num_rows"] == 2
    resp2 = client.get(f"/tabledata/?query_id={query_id}")
    assert resp2.status_code == 200
    returned2 = resp2.json()
    assert returned2["query_id"] == query_id
    assert returned2["userid"] == user_id
    assert returned2["num_rows"] == 2
