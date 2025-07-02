import os
import shutil
import pytest
from app.processing_operation import modular_processing_caller

# Use the same storage directory as the backend
STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app/storage'))
print(f"[DEBUG] TEST STORAGE_DIR: {STORAGE_DIR}")

def setup_module(module):
    # Only clean storage/temporary, do not delete other folders in storage
    temp_dir = os.path.join(STORAGE_DIR, 'temporary')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    # Only remove test PDFs matching new naming convention
    pdfs_dir = os.path.join(STORAGE_DIR, 'pdfs')
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir, exist_ok=True)
    for f in os.listdir(pdfs_dir):
        fpath = os.path.join(pdfs_dir, f)
        if os.path.isfile(fpath) and f.startswith('pdf_') and f.endswith('.pdf'):
            os.remove(fpath)

def test_move_query_pdfs_to_temp(tmp_path):
    import random
    pdfs_dir = os.path.join(STORAGE_DIR, 'pdfs')
    temp_dir = os.path.join(STORAGE_DIR, 'temporary')
    # Clean up pdfs_dir before test
    for f in os.listdir(pdfs_dir):
        fpath = os.path.join(pdfs_dir, f)
        if os.path.isfile(fpath):
            os.remove(fpath)
    # Use random user_id and query_id for isolation
    from uuid import uuid4
    user_id = random.randint(1000, 9999)
    query_id = random.randint(1000, 9999)
    filenames = [
        f"pdf_{user_id}_{query_id}_testa_{uuid4().hex}.pdf",
        f"pdf_{user_id}_{query_id}_testb_{uuid4().hex}.pdf",
        "unrelated.pdf"
    ]
    for fname in filenames:
        fpath = os.path.join(pdfs_dir, fname)
        print(f"[TEST DEBUG] Creating file: {fpath}")
        with open(fpath, 'wb') as f:
            f.write(b'%PDF-1.4\n%mock pdf content')
    print(f"[TEST DEBUG] pdfs_dir after creation: {os.listdir(pdfs_dir)}")
    # Move PDFs
    result_dir = modular_processing_caller.move_query_pdfs_to_temp(query_id)
    # Check that only the correct PDFs were moved
    assert os.path.exists(result_dir)
    moved = os.listdir(result_dir)
    print(f"[TEST DEBUG] Files moved to temp: {moved}")
    # Only files for this query_id should be moved
    assert any(f.startswith(f"pdf_{user_id}_{query_id}_testa_") for f in moved)
    assert any(f.startswith(f"pdf_{user_id}_{query_id}_testb_") for f in moved)
    # Unrelated PDF should remain in storage/pdfs
    assert 'unrelated.pdf' in os.listdir(pdfs_dir)
    # Clean up only the query temp dir
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    for fname in filenames:
        fpath = os.path.join(pdfs_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
