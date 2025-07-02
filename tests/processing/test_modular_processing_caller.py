import os
import shutil
import pytest
from app.processing_operation import modular_processing_caller

def setup_module(module):
    # Only clean storage/temporary, do not delete other folders in storage
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage/temporary'))
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    # Only remove test PDFs, do not delete any directories
    pdfs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage/pdfs'))
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir, exist_ok=True)
    for f in os.listdir(pdfs_dir):
        fpath = os.path.join(pdfs_dir, f)
        if os.path.isfile(fpath) and f.startswith('test_query_') and f.endswith('.pdf'):
            os.remove(fpath)

def test_move_query_pdfs_to_temp(tmp_path):
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage'))
    pdfs_dir = os.path.join(storage_dir, 'pdfs')
    temp_dir = os.path.join(storage_dir, 'temporary')
    query_id = 42
    # Create mock PDFs for this query in storage/pdfs
    filenames = [f'test_query_{query_id}_a.pdf', f'test_query_{query_id}_b.pdf', 'unrelated.pdf']
    for fname in filenames:
        with open(os.path.join(pdfs_dir, fname), 'wb') as f:
            f.write(b'%PDF-1.4\n%mock pdf content')
    # Move PDFs
    result_dir = modular_processing_caller.move_query_pdfs_to_temp(query_id)
    # Check that only the correct PDFs were moved
    assert os.path.exists(result_dir)
    moved = os.listdir(result_dir)
    assert f'test_query_{query_id}_a.pdf' in moved
    assert f'test_query_{query_id}_b.pdf' in moved
    # Unrelated PDF should remain in storage/pdfs
    assert 'unrelated.pdf' in os.listdir(pdfs_dir)
    # Clean up only the query temp dir
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    for fname in filenames:
        fpath = os.path.join(pdfs_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
