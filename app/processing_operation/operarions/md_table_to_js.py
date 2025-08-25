"""Convert markdown tables into a simple JSON structure for JS/front-end use.

Parses a markdown table and emits header and row arrays usable by the
frontend or other tooling.
"""
import re
import json

def parse_md_table(md_path: str):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Find the table start (first line with at least 2 pipes and not just dashes)
    table_start = None
    for i, line in enumerate(lines):
        if line.count('|') >= 2 and not all(c in '-| ' for c in line):
            table_start = i
            break
    if table_start is None:
        raise ValueError('No table found in markdown file.')

    # Parse header and rows
    header_line = lines[table_start]
    header_cells = [cell.strip() for cell in header_line.strip('|').split('|')]
    # Find the separator (---) line
    sep_idx = table_start + 1
    while sep_idx < len(lines) and not re.match(r'^\s*\|?\s*-+', lines[sep_idx]):
        sep_idx += 1
    # Parse data rows
    data_rows = []
    for line in lines[sep_idx+1:]:
        if line.count('|') >= 2:
            data_rows.append([cell.strip() for cell in line.strip('|').split('|')])
        else:
            break

    # Build mockHeaders
    mockHeaders = []
    for idx, title in enumerate(header_cells):
        mockHeaders.append({
            'value': f'col{idx}',
            'title': title
        })

    # Helper to extract meta from cell (e.g., "2021 @@loc_115@@" -> display: 2021, meta: loc_115)
    def parse_cell(cell: str):
        match = re.search(r'@@(loc_\d+)@@', cell)
        if match:
            meta = match.group(1)
            display = cell.replace(f'@@{meta}@@', '').strip()
        else:
            meta = None
            display = cell.strip()
        return {'display': display, 'meta': meta}

    # Build mockItems
    mockItems = []
    for row in data_rows:
        item = {}
        for idx, cell in enumerate(row):
            item[f'col{idx}'] = parse_cell(cell)
        mockItems.append(item)

    return mockHeaders, mockItems

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Parse markdown table to JS mockHeaders and mockItems.')
    parser.add_argument('md_path', help='Path to markdown file containing the table')
    parser.add_argument('--js', action='store_true', help='Output as JS code (default: JSON)')
    args = parser.parse_args()
    headers, items = parse_md_table(args.md_path)
    if args.js:
        print('const mockHeaders = ' + json.dumps(headers, indent=2) + ';')
        print('const mockItems = ' + json.dumps(items, indent=2) + ';')
    else:
        print(json.dumps({'mockHeaders': headers, 'mockItems': items}, indent=2))
