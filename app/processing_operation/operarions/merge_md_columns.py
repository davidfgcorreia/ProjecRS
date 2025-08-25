"""Merge columns inside markdown tables according to heuristics.

Transforms markdown table structures to combine columns when they represent
sub-parts of a single logical field.
"""

"""
Merge specified columns in markdown tables.
Given a directory containing markdown tables, merges the indicated columns in each table, placing their values in the same cell separated by ',' and updating the header accordingly.
"""

def merge_columns_in_md_file(input_file, output_file, columns_to_merge):
    """
    Merge specified columns (by index, 0-based) in a markdown table file.
    columns_to_merge: list of lists of column indices to merge, e.g. [[1,2],[6,7]]
    """
    import re
    def is_nonword(val):
        # Accept alphanumeric, dot, dash, percent, comma, and ignore pure symbols, empty, or '-----'
        return not re.search(r'[A-Za-z0-9.%]', val) or val.strip('-') == ''

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines or len(lines) < 2:
        return
    # Parse header
    header = [h.strip() for h in lines[0].strip('|').split('|')]
    # Build new header
    merged_indices_flat = set(i for group in columns_to_merge for i in group[1:])
    new_header = []
    i = 0
    while i < len(header):
        # Check if this index is the start of a merge group
        merge_group = None
        for group in columns_to_merge:
            if group[0] == i:
                merge_group = group
                break
        if merge_group:
            # Merge header names
            merged_names = [header[j] for j in merge_group]
            new_header.append('/'.join(merged_names))
            i += len(merge_group)
        elif i not in merged_indices_flat:
            new_header.append(header[i])
            i += 1
        else:
            i += 1
    # Separator row
    sep_row = '|' + '|'.join(['---'] * len(new_header)) + '|'
    # Process data rows
    data_lines = lines[1:]
    new_rows = []
    for line in data_lines:
        cells = [c.strip() for c in line.strip('|').split('|')]
        row = []
        i = 0
        while i < len(cells):
            # Check if this index is the start of a merge group
            merge_group = None
            for group in columns_to_merge:
                if group[0] == i:
                    merge_group = group
                    break
            if merge_group:
                merged_vals = []
                for j in merge_group:
                    val = cells[j] if j < len(cells) else ''
                    if not is_nonword(val):
                        merged_vals.append(val)
                row.append(' , '.join(merged_vals))
                i += len(merge_group)
            elif i not in merged_indices_flat:
                val = cells[i] if i < len(cells) else ''
                if not is_nonword(val):
                    row.append(val)
                else:
                    row.append('')
                i += 1
            else:
                i += 1
        # Pad row to header length
        if len(row) < len(new_header):
            row += [''] * (len(new_header) - len(row))
        new_rows.append('| ' + ' | '.join(row) + ' |')
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('| ' + ' | '.join(new_header) + ' |\n')
        f.write(sep_row + '\n')
        for row in new_rows:
            f.write(row + '\n')
