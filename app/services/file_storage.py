import os
from fastapi import UploadFile
from uuid import uuid4

STORAGE_DIR = os.path.join(os.path.dirname(__file__), '../storage')
PDF_DIR = os.path.join(STORAGE_DIR, 'pdfs')
RESULTS_DIR = os.path.join(STORAGE_DIR, 'results')
REPORTS_DIR = os.path.join(STORAGE_DIR, 'reports')

for d in [PDF_DIR, RESULTS_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

def save_pdf(upload_file: UploadFile, user_id: int, query_id: str) -> str:
    """
    Save uploaded PDF with a clear, accessible filename format:
    pdf_{user_id}_{query_id}_{original_filename}_{uuid}.pdf
    """
    original_filename = os.path.splitext(upload_file.filename or 'file.pdf')[0]
    ext = os.path.splitext(upload_file.filename or 'file.pdf')[1]
    unique_name = f"pdf_{user_id}_{query_id}_{original_filename}_{uuid4().hex}{ext}"
    file_path = os.path.join(PDF_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return unique_name

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
