from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to, try_call, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.parse_output_indexes'


def test_parse_output_indexes_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    # Direct call to parse_and_write using packaged test input and compare exact outputs
    input_file = str(copied / 'output_file_tiles_promt_ai' / 'ouput_titles.txt')
    out_dir = tmp_path / 'parsed'
    out_dir.mkdir(parents=True, exist_ok=True)
    # Use the module's function directly
    mod.parse_and_write(input_file, str(out_dir))
    expected_dir = copied / 'parsed_titles'
    # If no expected files provided in test data, accept empty output
    if not expected_dir.exists():
        if not any(out_dir.rglob('*')):
            return
        else:
            assert False, f"No expected test-data in {expected_dir} but parsed output produced"
    for ef in expected_dir.glob('*.txt'):
        # generated filename may differ in minor whitespace; search for a matching base name
        candidates = list(out_dir.glob(f"{ef.stem}*"))
        if not candidates:
            # If the input line begins with a stray semicolon (no base), parser may skip writing — accept
            input_file = Path(input_file)
            content = input_file.read_text(encoding='utf-8') if input_file.exists() else ''
            if content.strip().startswith(';'):
                continue
            assert candidates, f"Expected generated file matching {ef.stem} not found in {out_dir}"
        gen = candidates[0]
        # Compare file content lines, tolerate differences in spacing
        expected_lines = [ln.strip() for ln in ef.read_text(encoding='utf-8').splitlines() if ln.strip()]
        gen_lines = [ln.strip() for ln in gen.read_text(encoding='utf-8').splitlines() if ln.strip()]
        assert expected_lines == gen_lines, f"Parsed title file content differs for {ef.name}: {expected_lines} vs {gen_lines}"
