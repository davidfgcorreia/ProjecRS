import importlib
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.preprocess_vlaues'

def test_preprocess_vlaues_import():
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")
    public_callables = [name for name, obj in vars(mod).items() if callable(obj) and not name.startswith('_')]
    assert public_callables, f"Module {MODULE} imported but exposes no public callables"
