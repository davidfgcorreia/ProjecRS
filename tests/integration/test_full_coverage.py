import pytest
from fastapi.testclient import TestClient
import uuid
from app.main import app

client = TestClient(app)

def create_user(name, email, password="testpass"):
    return client.post("/users/", json={"name": name, "email": email, "password": password})

def test_get_users():
    email = f"user_{uuid.uuid4().hex}@example.com"
    create_user("User1", email)
    resp = client.get("/users/")
    assert resp.status_code == 200

def test_get_user_by_id():
    email = f"user_{uuid.uuid4().hex}@example.com"
    user = create_user("User2", email).json()
    resp = client.get(f"/users/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == email

def test_get_user_by_id_not_found():
    resp = client.get("/users/999999")
    assert resp.status_code == 404

def test_update_user():
    email = f"user_{uuid.uuid4().hex}@example.com"
    user = create_user("User3", email).json()
    new_email = f"updated_{email}"
    resp = client.put(f"/users/{user['id']}", json={"name": "Updated", "email": new_email, "password": "newpass"})
    assert resp.status_code == 200
    assert resp.json()["email"] == new_email

def test_update_user_not_found():
    resp = client.put("/users/999999", json={"name": "X", "email": "x@x.com", "password": "x"})
    assert resp.status_code == 404

def test_delete_user():
    email = f"user_{uuid.uuid4().hex}@example.com"
    user = create_user("User4", email).json()
    resp = client.delete(f"/users/{user['id']}")
    assert resp.status_code == 200
    resp2 = client.get(f"/users/{user['id']}")
    assert resp2.status_code == 404

def test_delete_user_not_found():
    resp = client.delete("/users/999999")
