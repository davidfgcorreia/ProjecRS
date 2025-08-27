from pathlib import Path
import sys
import pytest

from tests.processing.helpers import copy_query_to, assert_dir_has_files

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.processing_operation.operarions.find_section_by_marker import main as find_section_main


def test_find_section_by_marker_runs(tmp_path: Path):
    # copy sample query into tmp workspace
    copied = copy_query_to(tmp_path)
    # choose storage paths from copied query
    pdfs_dir = copied / 'pdfs'
    md_dir = copied / 'markdown'
    out_pdf = tmp_path / 'find_marker_out.pdf'

    # run main using a marker key present in the sample localization map (e.g. loc_2)
    # use the @@loc_2@@ style which the module supports
    find_section_main(str(pdfs_dir), str(md_dir), '@@loc_2@@', str(out_pdf), None)

    # validate output PDF exists (or at least file was created)
    assert out_pdf.exists()
