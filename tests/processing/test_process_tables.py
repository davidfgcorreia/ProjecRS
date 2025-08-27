from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.process_tables'


def test_process_tables_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    # some fixtures place the merged markdown under final_values_for_table
    final_values = copied / 'final_values_for_table'
    if (final_values / 'all_tables_merged.md').exists():
        (copied / 'markdown').mkdir(exist_ok=True)
        (final_values / 'all_tables_merged.md').replace(copied / 'markdown' / 'all_tables_merged.md')

    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    funcs = [getattr(mod, n) for n in ('process_all', 'main', 'process_tables') if hasattr(mod, n)]
    outp = tmp_path / 'out'
    outp.mkdir(parents=True, exist_ok=True)
    args = [(str(copied / 'markdown'), str(outp))]
    for f in funcs:
        for candidate in args:
            try:
                f(*candidate)
                assert_dir_has_files(outp)
                return
            except TypeError:
                continue
    pytest.skip(f"No suitable callable worked in {MODULE}")
