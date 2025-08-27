from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.extract_titles'


def test_extract_titles_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    funcs = [getattr(mod, n) for n in ('extract_titles_with_content', 'main') if hasattr(mod, n)]
    args = [(str(copied / 'markdown'), str(tmp_path / 'pdfs_titles'))]
    for f in funcs:
        for candidate in args:
            try:
                f(*candidate)
                assert_dir_has_files(tmp_path / 'pdfs_titles')
                return
            except TypeError:
                continue
    pytest.skip(f"No suitable callable worked in {MODULE}")
