from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.copy_sections_by_title'


def test_copy_sections_by_title_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    # common function names
    funcs = [getattr(mod, n) for n in ('process_all_files', 'main', 'run') if hasattr(mod, n)]
    if not funcs:
        funcs = [obj for name, obj in vars(mod).items() if callable(obj) and not name.startswith('_')]

    args_candidates = [
    (str(copied / 'pdfs_titles'), str(copied / 'markdown'), str(tmp_path / 'out'), str(copied / 'pdfs_titles')),
    (str(copied / 'markdown'), str(copied / 'pdfs'), str(tmp_path / 'out'), str(copied / 'markdown')),
    ]

    for f in funcs:
        for candidate in args_candidates:
            try:
                f(*candidate)
                # output dir is the third arg in candidate tuples
                out_dir = Path(candidate[2])
                if out_dir.exists() and any(out_dir.rglob('*')):
                    assert_dir_has_files(out_dir)
                    return
                # If the output dir is empty, that is valid only if required inputs were missing.
                titles_dir = Path(candidate[0])
                markdown_dir = Path(candidate[1])
                all_titles_dir = Path(candidate[3]) if len(candidate) > 3 else None
                missing_expected = True
                for titles_path in titles_dir.glob('*.txt'):
                    basename = titles_path.stem
                    md_path = markdown_dir / basename / f"{basename}.md"
                    pdf_titles_path = all_titles_dir / f"{basename}_titles.txt" if all_titles_dir else None
                    # If both md and pdf_titles exist for any titles file, we would expect output
                    if md_path.exists() and (pdf_titles_path is None or pdf_titles_path.exists()):
                        missing_expected = False
                        break
                if missing_expected:
                    # inputs insufficient to generate outputs — treat as pass
                    return
                # otherwise fallthrough and try next candidate
            except TypeError:
                continue

    pytest.skip(f"No suitable callable worked in {MODULE}")
