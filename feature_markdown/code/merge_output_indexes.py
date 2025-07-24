"""
This script merges two sets of parsed output files (one per study) in the new format.
For each study, it keeps the formatting and key order of the first file (parsed from output_indexes.txt),
fills empty values with those from the second file (parsed from output_indexes2.txt),
and writes the merged result to storage/final_values_for_tables/parsed_per_study.
"""

import os

PARSED1_DIR = "../storage/parsed_output_tables"
PARSED2_DIR = "../storage/parsed_index_2"
OUTPUT_DIR = "../storage/final_values_for_tables"

def parse_file(filepath):
    """
    Parse a single study file in the format:
    restrictors: [restrictors]   (optional)
    key: value
    key: value
    ...
    Returns (restrictors, [(key, value), ...])
    """
    restrictors = None
    kv_list = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if line.startswith("restrictors:") or line.startswith("main_restrictors"):
                restrictors = line.split(":", 1)[1].strip()
            elif ":" in line:
                k, v = line.split(":", 1)
                kv_list.append((k.strip(), v.strip()))
    return restrictors, kv_list

def parse_file_to_dict(filepath):
    """
    Parse a study file into a dict {key: value}, ignoring order.
    """
    d = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("restrictors:") or line.startswith("main_restrictors"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
    return d

def get_study_files(directory):
    """
    Return a dict {normalized_basename: full_path} for all .txt files in directory.
    Normalization: replace spaces with underscores and remove file extension.
    """
    files = {}
    for fname in os.listdir(directory):
        if fname.endswith(".txt"):
            norm = fname.replace(" ", "_").replace(".txt", "")
            files[norm] = os.path.join(directory, fname)
    return files

def merge_study_files(file1, file2, out_path):
    """
    Merge two study files, keeping the order and formatting of file1,
    filling empty values with those from file2.
    """
    restrictors1, kv_list1 = parse_file(file1)
    d2 = parse_file_to_dict(file2) if file2 and os.path.exists(file2) else {}

    import re
    with open(out_path, "w", encoding="utf-8") as f:
        if restrictors1:
            f.write(f"restrictors: {restrictors1}\n")
        for k, v in kv_list1:
            v2 = d2.get(k, "")
            if v and v2:
                value = f"{v} {v2}".strip()
            elif v:
                value = v
            else:
                value = v2
            # Remove space between closing parenthesis and percent (e.g., ')) 0.1%')
            value = re.sub(r'\)\s+(\d+\.?\d*%)', r')\1', value)
            f.write(f"{k}: {value}\n")
        # Add any extra keys from file2 not in file1
        keys1 = set(k for k, _ in kv_list1)
        for k, v in d2.items():
            # Remove space for extra keys as well
            v = re.sub(r'\)\s+(\d+\.?\d*%)', r')\1', v)
            if k not in keys1:
                f.write(f"{k}: {v}\n")

def main(parsed1_dir=None, parsed2_dir=None, output_dir=None):
    import sys
    # Allow CLI args: parsed1_dir parsed2_dir output_dir
    if parsed1_dir is None or parsed2_dir is None or output_dir is None:
        if len(sys.argv) >= 4:
            parsed1_dir = sys.argv[1]
            parsed2_dir = sys.argv[2]
            output_dir = sys.argv[3]
        else:
            parsed1_dir = PARSED1_DIR
            parsed2_dir = PARSED2_DIR
            output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    files1 = get_study_files(parsed1_dir)
    files2 = get_study_files(parsed2_dir)

    for norm_name, file1 in files1.items():
        file2 = files2.get(norm_name)
        out_fname = os.path.basename(file1)
        out_path = os.path.join(output_dir, out_fname)
        merge_study_files(file1, file2, out_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main()
