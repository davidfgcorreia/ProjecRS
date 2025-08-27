from pathlib import Path
import sys
import importlib
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_merge_columns_merges_two_columns_directly():
    """Create a small mock table object in-file and call merge_columns(table, col1, col2).

    Verifies headers are merged and the second column is removed, with cell values
    and metadata concatenated as implemented by the function.
    """
    mod = importlib.import_module('app.processing_operation.operarions.merge_columns')
    assert hasattr(mod, 'merge_columns'), 'merge_columns function not found'
    merge_columns = getattr(mod, 'merge_columns')

    # Build a mock table object expected by the function
    class MockTable:
        def __init__(self, columns_content, row_ids):
            self.columns_content = columns_content
            self.row_ids = row_ids

    # columns order matters because the function inspects the first row's keys
    columns_content = [
        {
            'col0': 'X0',
            'colA': {'display': 'A1', 'meta': 'MA1'},
            'colB': {'display': 'B1', 'meta': 'MB1'},
            'colC': 'C1',
        },
        {
            'col0': 'X1',
            'colA': {'display': 'A2', 'meta': 'MA2'},
            'colB': {'display': 'B2', 'meta': 'MB2'},
            'colC': 'C2',
        },
    ]

    # Row ids must be long enough; header_idx1 and header_idx2 are computed from column indexes
    row_ids = ['Header0', 'Header1', 'Header2', 'Header3']

    table = MockTable(columns_content=columns_content, row_ids=row_ids)

    # Call merge_columns to merge the content keys 'colA' and 'colB'
    merged = merge_columns(table, 'colA', 'colB')

    # After merge, colB should be removed and colA should be a dict with merged display/meta
    # Validate values exactly for each row
    expected_displays = ['A1 , B1', 'A2 , B2']
    expected_metas = ['MA1, MB1', 'MA2, MB2']
    for i, row in enumerate(merged.columns_content):
        assert 'colB' not in row, 'colB should have been removed'
        assert 'colA' in row, 'colA must still exist after merge'
        val = row['colA']
        assert isinstance(val, dict), 'colA value should be a dict after merge'
        assert val.get('display') == expected_displays[i]
        assert val.get('meta') == expected_metas[i]

    # Check headers: merged header must be exactly 'Header0 / Header1'
    assert merged.row_ids[0] == 'Header0 / Header1'
    assert len(merged.row_ids) == 3, 'one header entry should have been removed'
