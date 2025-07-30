"""
Base script to generate a markdown table from a key-value text file with branch notation.
This script reads the input file, extracts headers (indexes), and prepares for table generation.
You can implement the row/branch logic as needed.
"""
from pathlib import Path
import re

def parse_branch_value(value):
    """Parse a value string into (branch_tuple, value) pairs."""
    results = []
    for part in value.split('//'):
        part = part.strip()
        m = re.match(r'\(\((.*?)\)\)\s*(.*)', part)
        if m:
            branch = tuple(b.strip() for b in m.group(1).split(','))
            val = m.group(2).strip()
            results.append((branch, val))
        elif part:
            results.append(((), part))
    return results


def parse_key_value_file_lines(lines):
    data = {}
    keys = []
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        data[key] = parse_branch_value(value)
        keys.append(key)
    return data, keys


def build_lines_branches(data, keys):
    lines_branches = []
    for k in range(len(keys)):
        for i in range(len(data[keys[k]])):
            branch, val = data[keys[k]][i]
            if not branch:
                continue
            if len(lines_branches) <= i:
                lines_branches.append([branch])
            elif branch not in lines_branches[i]:
                lines_branches[i].append(branch)
    for i in range(len(lines_branches)):
        lines_branches[i].sort(key=lambda b: (-len(b), b))
    return lines_branches

def build_index_branch_names(data, keys):
    index_branch_names = []
    seen = set()
    for k in keys:
        branch_names = set()
        for branch, val in data[k]:
            if branch:
                branch_names.add(branch[-1])
        if branch_names:
            frozen = frozenset(branch_names)
            if frozen not in seen:
                index_branch_names.append(sorted(branch_names))
                seen.add(frozen)
    return index_branch_names

def resolve_conflicts(lines_branches, index_branch_names, main_branches=None):

    aditional_branches = []
    if main_branches:
        for branch in main_branches:
            if branch not in index_branch_names:
                aditional_branches.append(branch[0])
        index_branch_names += [aditional_branches]

    conflicts_found = True
    while conflicts_found:
        conflicts_found = False
        for k in range(len(lines_branches)):
            # If any branch in the row has more than one identifier, all must share the same principal identifier
            max_identifiers = max((len(branch) for branch in lines_branches[k] if branch), default=1)
            if max_identifiers > 1:
                # Prioritize the first principal identifier in the row
                principal_ids = [branch[0] for branch in lines_branches[k] if branch]
                if len(set(principal_ids)) > 1:
                    keep_id = principal_ids[0]
                    # Move all branches with other principal identifiers to the next line, preserving order
                    for branch in list(lines_branches[k]):
                        if branch and branch[0] != keep_id:
                            print(f"Conflict detected in row {k}: splitting branch {branch}")
                            lines_branches[(k + 1) % len(lines_branches)].append(branch)
                            lines_branches[k].remove(branch)
                            conflicts_found = True
            # Continue with original conflict logic
            conter = 0
            while True:
                branhequals = []
                can_compare = False
                for branch in lines_branches[k]:
                    for i in range(len(index_branch_names)):
                        if len(branch) > conter and branch[conter] in index_branch_names[i]:
                            branhequals.append(i)
                            can_compare = True
                if not can_compare:
                    break
                compaux = []
                for i in range(len(branhequals)):
                    while len(compaux) <= branhequals[i]:
                        compaux.append([])
                    if i < len(lines_branches[k]) and conter < len(lines_branches[k][i]):
                        compaux[branhequals[i]].append(lines_branches[k][i][conter])
                    else:
                        continue
                compaux = [lst for lst in compaux if lst]
                for i in range(len(compaux)):
                    if not compaux:
                        continue
                    for j in range(len(compaux[i])):
                        if compaux[i][j] != compaux[i][0]:
                            t = 0
                            for t in range(len(lines_branches[k])):
                                if compaux[i][j] in lines_branches[k][t]:
                                    break
                            print(f"Conflict detected in row {k}: splitting branch {lines_branches[k][t]}")
                            lines_branches[(k + 1) % len(lines_branches)].append(lines_branches[k][t])
                            lines_branches[k].pop(t)
                            conflicts_found = True
                conter += 1
    return lines_branches

def build_table(data, keys, lines_branches, main_branches):
    table = [['' for _ in range(len(keys))] for _ in range(max(len(lines_branches), 1))]
    # Identify frequency-like columns
    freq_like_patterns = ['frequency', 'freq', 'interval']
    for k, key in enumerate(keys):
        is_freq_col = any(pat in key.lower() for pat in freq_like_patterns)
        # Check if only one value without branch exists for this key
        non_branch_vals = [val for branch, val in data[key] if not branch]
        branch_vals = [val for branch, val in data[key] if branch]
        if is_freq_col and len(non_branch_vals) == 1 and not branch_vals and k > 0:
            # Only fill the cell if the previous column (k-1) has a real non-empty value in the same row
            for row in table:
                if not row[k] and row[k-1]:
                    row[k] = non_branch_vals[0]
            continue
        for i, (branch, val) in enumerate(data[key]):
            if not branch:
                if main_branches:
                    # Place value in the first line where each main restrictor appears in lines_branches
                    for mains in main_branches:
                        placed = False
                        for c, branches in enumerate(lines_branches):
                            for branch in branches:
                                # Compare only the first and only value inside the tuple
                                if branch and len(branch) > 0 and branch[0] == mains[0]:
                                    table[c][k] = val
                                    placed = True
                                    break
                            if placed:
                                break
                else:
                    # Place value only in the first line (row 0) if no main restrictors
                    table[0][k] = val
            else:
                for c, branches in enumerate(lines_branches):
                    if branch in branches:
                        table[c][k] = val
                        break
    return table

def build_first_column(table, lines_branches, main_branches, file_label):
    first_column = ['' for _ in range(max(len(lines_branches), 1))]
    if main_branches:
        used = set()
        for mains in main_branches:
            for i, branches in enumerate(lines_branches):
                if i in used:
                    continue
                for branch in branches:
                    if branch and branch[0] == mains[0]:
                        first_column[i] = f"{file_label} [{mains[0]}]"
                        used.add(i)
                        break
                if i in used:
                    break
    else:
        first_column[0] = file_label
    return first_column

def write_merged_table(all_tables, output_dir):
    out_path = output_dir / 'all_tables_merged.md'
    if all_tables:
        merged_keys = all_tables[0][2]
        headers = ['File'] + merged_keys
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('| ' + ' | '.join(headers) + ' |\n')
            f.write('|' + '|'.join(['-' * max(4, len(k)) for k in headers]) + '|\n')
            for idx, (first_coloumn, table, keys) in enumerate(all_tables):
                for i in range(len(table)):
                    row = [first_coloumn[i]] + [table[i][j] if j < len(table[i]) else '' for j in range(len(merged_keys))]
                    f.write('| ' + ' | '.join(row) + ' |\n')
        print(f"Merged table written to {out_path}")

def main(input_dir=None, output_dir=None):
    import sys
    if input_dir is None or output_dir is None:
        if len(sys.argv) >= 3:
            input_dir = Path(sys.argv[1])
            output_dir = Path(sys.argv[2])
        else:
            input_dir = Path('../storage/final_values_for_tables')
            output_dir = Path('../storage/final_values_for_table')
    else:
        if isinstance(input_dir, str):
            input_dir = Path(input_dir)
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

    input_files = sorted(input_dir.glob('*.txt'))
    all_filenames = []
    all_tables = []

    for in_path in input_files:
        with open(in_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        main_branches = []
        data_start = 0
        # Skip empty or comment lines at the top
        while data_start < len(lines) and (not lines[data_start].strip() or lines[data_start].strip().startswith('#')):
            data_start += 1
        # Check for main_restrictors or restrictors at the first non-empty line
        if data_start < len(lines) and (lines[data_start].strip().startswith("main_restrictors") or lines[data_start].strip().startswith("restrictors")):
            m = re.match(r"(?:main_restrictors|restrictors)\s*:\s*\[([^\]]*)\]", lines[data_start].strip())
            if m:
                restrictors = [r.strip() for r in m.group(1).split(',') if r.strip()]
                main_branches = [tuple([r]) for r in restrictors]
            data_start += 1
        # Always parse from the first data line after restrictors (or from the top if not present)
        data, keys = parse_key_value_file_lines(lines[data_start:])
        lines_branches = build_lines_branches(data, keys)
        index_branch_names = build_index_branch_names(data, keys)
        lines_branches = resolve_conflicts(lines_branches, index_branch_names,main_branches)
        table = build_table(data, keys, lines_branches, main_branches)
        file_label = in_path.stem.replace('_', ' ').strip()
        first_column = build_first_column(table, lines_branches, main_branches, file_label)
        all_filenames.append(in_path.stem)
        all_tables.append((first_column, table, keys))

    write_merged_table(all_tables, output_dir)


if __name__ == "__main__":
    main()
