import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_get_result_table_not_found():
    resp = client.get("/result/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Query not found"

def test_get_report_not_found():
    resp = client.get("/result/report/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Query not found"

def test_get_table_info_not_found():
    resp = client.get("/result/table-info/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Query not found"
