import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
# Prefer packaged test data (comparation files) if available; otherwise fall back to app/storage/temporary
TEST_DATA_STORAGE = ROOT / 'tests' / 'test_data' / 'comparation files' / 'storage'
TEST_DATA_TEMP = TEST_DATA_STORAGE / 'temporary'


def pick_sample_query_dir() -> Path:
    """Return the first query_* directory path from packaged test data only.

    This intentionally does not fall back to live storage. The test harness
    should use the provided test fixtures under `tests/test_data`.
    """
    if TEST_DATA_TEMP.exists():
        for child in TEST_DATA_TEMP.iterdir():
            if child.is_dir() and child.name.startswith('query_'):
                return child
    raise FileNotFoundError(f"No query_* directory found in {TEST_DATA_TEMP}")


def copy_query_to(tmp_root: Path) -> Path:
    """Copy a sample query directory into tmp_root and return the copied path."""
    src = pick_sample_query_dir()
    dest = tmp_root / src.name
    shutil.copytree(src, dest)
    return dest


def copy_storage_subdir(subdir: str, tmp_root: Path) -> Path:
    """Copy a top-level storage subdirectory from packaged test data into tmp_root.

    Example subdir: 'pdfs', 'markdowns', 'temporary'
    """
    src = TEST_DATA_STORAGE / subdir
    if not src.exists():
        raise FileNotFoundError(f"Requested storage subdir not found in test data: {src}")
    dest = tmp_root / subdir
    shutil.copytree(src, dest)
    return dest


def try_call(func, candidates):
    """Try calling func with each tuple of args in candidates.

    Returns True if any call succeeds, False otherwise.
    The function exceptions other than TypeError are propagated, since they
    indicate the function ran but failed for other reasons.
    """
    for args in candidates:
        try:
            func(*args)
            return True
        except TypeError:
            # wrong signature, try next
            continue
    return False


def assert_dir_has_files(p: Path) -> None:
    """Assert that path exists and contains at least one file (recursively)."""
    if not p.exists():
        raise AssertionError(f"Expected path does not exist: {p}")
    for _ in p.rglob('*'):
        return
    raise AssertionError(f"Expected path {p} to contain files but it is empty")
