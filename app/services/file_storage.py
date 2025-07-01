import os
from fastapi import UploadFile
from uuid import uuid4
from typing import Optional

STORAGE_DIR = os.path.join(os.path.dirname(__file__), '../storage')
PDF_DIR = os.path.join(STORAGE_DIR, 'pdfs')
TEMP_DIR = os.path.join(STORAGE_DIR, 'temp')
RESULTS_DIR = os.path.join(STORAGE_DIR, 'results')
REPORTS_DIR = os.path.join(STORAGE_DIR, 'reports')

for d in [PDF_DIR, TEMP_DIR, RESULTS_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

def save_pdf(upload_file: UploadFile) -> str:
    filename = upload_file.filename or 'file.pdf'
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid4().hex}{ext}"
    file_path = os.path.join(PDF_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return unique_name

def save_temp_file(content: bytes, suffix: str = "") -> str:
    filename = f"{uuid4().hex}{suffix}"
    file_path = os.path.join(TEMP_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return filename

def save_result(content: bytes, suffix: str = "") -> str:
    filename = f"{uuid4().hex}{suffix}"
    file_path = os.path.join(RESULTS_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return filename

def save_report(content: str) -> str:
    filename = f"{uuid4().hex}.txt"
    file_path = os.path.join(REPORTS_DIR, filename)
    with open(file_path, "w") as f:
        f.write(content)
    return filename

def get_pdf_path(filename: str) -> str:
    return os.path.join(PDF_DIR, filename)

def get_result_path(filename: str) -> str:
    return os.path.join(RESULTS_DIR, filename)

def get_report_path(filename: str) -> str:
    return os.path.join(REPORTS_DIR, filename)
