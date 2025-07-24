def preprocess_step2_fill_missing_by_first_name(lines):
    """
    For each group of keys with the same first part (name1 in name1-name2),
    find the max number of values and branches, then fill missing values for each branch with '-----'.
    """
    processed_lines = []
    data_lines = lines
    # Always preserve the first line if it is a main_restrictors or restrictors line
    if lines and (lines[0].strip().startswith("main_restrictors") or lines[0].strip().startswith("restrictors")):
        processed_lines.append(lines[0].rstrip())
        data_lines = lines[1:]

    # Group keys by first part before dash
    from collections import defaultdict
    key_groups = defaultdict(list)
    for idx, line in enumerate(data_lines):
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        first = key.split('-', 1)[0] if '-' in key else key
        key_groups[first].append((idx, key, value.strip()))

    # For each group, find all branches and max number of values for each key
    new_lines = list(data_lines)
    for group_keys in key_groups.values():
        # Collect all branches in this group
        all_branches = set()
        max_count = 0
        parsed_per_key = {}
        for idx, key, value in group_keys:
            parsed = parse_branch_value(value)
            parsed_per_key[key] = parsed
            for branch, val in parsed:
                if branch:  # Only count non-empty branches
                    all_branches.add(branch)
            # Count values per branch (excluding no-branch)
            branch_counts = defaultdict(int)
            for branch, val in parsed:
                if branch:
                    branch_counts[branch] += 1
            if branch_counts:
                max_count = max(max_count, max(branch_counts.values()))
        # For each key in the group, fill missing values for each branch
        for idx, key, value in group_keys:
            parsed = parsed_per_key[key]
            # If there is only one value and it has no branch, do not change this line
            if len(parsed) == 1 and not parsed[0][0]:
                continue
            # Map branch to list of values
            branch_to_vals = defaultdict(list)
            for branch, val in parsed:
                branch_to_vals[branch].append(val)
            parts = []
            for branch in sorted(all_branches):
                vals = branch_to_vals.get(branch, [])
                for i in range(max_count):
                    if i < len(vals):
                        v = vals[i]
                    else:
                        v = '-----'
                    branch_str = ','.join(branch)
                    parts.append(f"(({'{}'.format(branch_str)})){v}")
            # If there are also no-branch values, append them as-is (do not fill)
            if () in branch_to_vals:
                for v in branch_to_vals[()]:
                    parts.append(v)
            new_lines[idx] = f"{key}: {' // '.join(parts)}"

    processed_lines.extend(new_lines)
    return processed_lines
"""
Preprocess key-value files: Multi-step pipeline.
Step 1: For each key, if all values (across branches) are the same, remove branch notation and keep only one value.
Output files are written to a new directory, preserving filenames.
Add additional steps as needed in the pipeline.
"""
from pathlib import Path
import re
import os


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


def preprocess_step1_remove_branch_if_all_same(lines):
    """
    Step 1: For each key, if all values (across branches) are the same, remove branch notation and keep only one value.
    Returns a list of processed lines.
    """
    processed_lines = []
    data_lines = lines
    # Always preserve the first line if it is a main_restrictors or restrictors line
    if lines and (lines[0].strip().startswith("main_restrictors") or lines[0].strip().startswith("restrictors")):
        processed_lines.append(lines[0].rstrip())
        data_lines = lines[1:]
    for line in data_lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        parsed = parse_branch_value(value)
        values = [v for b, v in parsed if v]
        unique_values = set(values)
        if len(unique_values) == 1 and len(values) > 1:
            # All values are the same, output as key: value (no branch)
            processed_lines.append(f"{key}: {list(unique_values)[0]}")
        else:
            # Keep original line
            processed_lines.append(f"{key}: {value}")
    return processed_lines

def preprocess_pipeline(lines):
    """
    Run all preprocessing steps in order. Add new steps here as needed.
    """
    lines = preprocess_step1_remove_branch_if_all_same(lines)
    # Step 2: fill missing by first name
    lines = preprocess_step2_fill_missing_by_first_name(lines)
    # Step 1: remove branch if all values are the same
    lines = preprocess_step1_remove_branch_if_all_same(lines)
    return lines

def preprocess_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    processed_lines = preprocess_pipeline(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        for l in processed_lines:
            f.write(l + '\n')


def preprocess_directory(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for file in input_dir.glob('*.txt'):
        preprocess_file(file, output_dir / file.name)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        preprocess_directory(sys.argv[1], sys.argv[2])
    else:
        os.makedirs('../main_storage/exemple/preprocessed_values', exist_ok=True)
        preprocess_directory('../main_storage/exemple/final_values_for_tables', '../main_storage/exemple/preprocessed_values')
