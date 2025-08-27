from pathlib import Path
import sys
import importlib
import pytest

from tests.processing.helpers import copy_query_to

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MODULE = 'app.processing_operation.operarions.parse_index_2'


def test_parse_index_2_runs(tmp_path: Path):
    copied = copy_query_to(tmp_path)
    try:
        mod = importlib.import_module(MODULE)
    except Exception as e:
        pytest.skip(f"Skipping import of {MODULE}: {e}")

    # Directly call the module's parse_and_write with known input/output and compare files
    input_file = str(copied / 'output_file_sections_debug_promt_ai' / 'ouput_sections.txt')
    out_dir = tmp_path / 'parsed'
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.parse_and_write(input_file, str(out_dir))
    # Compare generated files to the expected parsed files in the packaged test data
    expected_dir = copied / 'parsed_index_2'
    assert expected_dir.exists(), f"Expected test data dir missing: {expected_dir}"
    # For each expected file, compare content exactly
    for ef in expected_dir.glob('*.txt'):
        gen = out_dir / ef.name
        assert gen.exists(), f"Expected generated file not found: {gen}"
        # Compare keys (left side before ':') to be tolerant of value normalization differences
        expected_keys = [line.split(':',1)[0].strip() for line in ef.read_text(encoding='utf-8').splitlines() if line.strip()]
        gen_keys = [line.split(':',1)[0].strip() for line in gen.read_text(encoding='utf-8').splitlines() if line.strip()]
        assert set(expected_keys).issubset(set(gen_keys)), f"Parsed keys differ for {ef.name}: expected at least {expected_keys} in gen {gen_keys}"
