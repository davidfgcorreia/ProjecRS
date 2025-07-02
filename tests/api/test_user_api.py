import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_create_user():
    unique_email = f"testuser_{uuid.uuid4().hex}@example.com"
    response = client.post("/users/", json={"name": "Test User", "email": unique_email, "password": "testpass"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == unique_email

def test_upload_pdf(monkeypatch):
    unique_email = f"fileuser_{uuid.uuid4().hex}@example.com"
    user_resp = client.post("/users/", json={"name": "File User", "email": unique_email, "password": "testpass"})
    assert user_resp.status_code == 200
    user_id = user_resp.json()["id"]
    file_content = b"%PDF-1.4 test pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    response = client.post(f"/upload/pdf/?user_id={user_id}", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"].endswith(".pdf")
    assert data["user_id"] == user_id
    assert "query_id" in data

def test_get_result_table(monkeypatch):
    unique_email = f"queryuser_{uuid.uuid4().hex}@example.com"
    user_resp = client.post("/users/", json={"name": "Query User", "email": unique_email, "password": "testpass"})
    assert user_resp.status_code == 200
    user_id = user_resp.json()["id"]
    response = client.get("/result/99999")
    assert response.status_code == 404
