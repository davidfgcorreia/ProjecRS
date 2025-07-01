import os
import pytest
from fastapi import UploadFile
from io import BytesIO
from app.services import file_storage

def test_save_pdf_and_get_path(tmp_path, monkeypatch):
    monkeypatch.setattr(file_storage, "PDF_DIR", tmp_path)
    content = b"%PDF-1.4 test pdf content"
    upload = UploadFile(filename="test.pdf", file=BytesIO(content))
    filename = file_storage.save_pdf(upload)
    assert filename.endswith(".pdf")
    path = file_storage.get_pdf_path(filename)
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == content

def test_save_temp_file(tmp_path, monkeypatch):
    monkeypatch.setattr(file_storage, "TEMP_DIR", tmp_path)
    content = b"temp content"
    filename = file_storage.save_temp_file(content, ".tmp")
    assert filename.endswith(".tmp")
    path = os.path.join(tmp_path, filename)
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == content

def test_save_result(tmp_path, monkeypatch):
    monkeypatch.setattr(file_storage, "RESULTS_DIR", tmp_path)
    content = b"result content"
    filename = file_storage.save_result(content, ".res")
    assert filename.endswith(".res")
    path = os.path.join(tmp_path, filename)
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == content

def test_save_report(tmp_path, monkeypatch):
    monkeypatch.setattr(file_storage, "REPORTS_DIR", tmp_path)
    content = "report content"
    filename = file_storage.save_report(content)
    assert filename.endswith(".txt")
    path = os.path.join(tmp_path, filename)
    assert os.path.exists(path)
    with open(path, "r") as f:
        assert f.read() == content
