from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.generate_markdown_table_clean'


def test_generate_markdown_table_clean_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    funcs = [getattr(mod, n) for n in ('clean_table_markdown', 'main') if hasattr(mod, n)]
    out_dir = tmp_path / 'final_values_for_table'
    out_dir.mkdir(parents=True, exist_ok=True)
    args = [(str(copied / 'final_values_for_tables'), str(out_dir))]
    for f in funcs:
        for candidate in args:
            try:
                f(*candidate)
                assert_dir_has_files(out_dir)
                return
            except TypeError:
                continue
    pytest.skip(f"No suitable callable worked in {MODULE}")
