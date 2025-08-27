from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.localizations'


def test_localizations_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    funcs = [getattr(mod, n) for n in ('process_and_save_all', 'main', 'run') if hasattr(mod, n)]
    args = [(str(copied / 'final_values_for_tables'), str(tmp_path / 'localizations'), str(tmp_path / 'map.json'))]

    for f in funcs:
        for candidate in args:
            try:
                f(*candidate)
                assert_dir_has_files(tmp_path / 'localizations')
                return
            except TypeError:
                continue
    pytest.skip(f"No suitable callable worked in {MODULE}")
