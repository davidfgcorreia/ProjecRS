import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def create_user():
    email = f"upload_{uuid.uuid4().hex}@example.com"
    resp = client.post("/users/", json={"name": "UploadUser", "email": email, "password": "testpass"})
    assert resp.status_code == 200
    return resp.json()["id"]

def test_upload_pdf_success():
    user_id = create_user()
    file_content = b"%PDF-1.4 test pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    resp = client.post(f"/upload/pdf/?user_id={user_id}", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"].endswith(".pdf")
    assert data["user_id"] == user_id
    assert "query_id" in data

def test_upload_pdf_user_not_found():
    files = {"file": ("test.pdf", b"%PDF-1.4 test pdf content", "application/pdf")}
    resp = client.post("/upload/pdf/?user_id=999999", files=files)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"
