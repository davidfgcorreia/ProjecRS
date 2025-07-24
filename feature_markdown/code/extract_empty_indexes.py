import os
from pathlib import Path

def extract_empty_indexes_from_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    empty_indexes = []
    main_restrictors_line = None
    # Check if the first line contains main restrictors in the format: main_restrictors : [restrictors]
    if lines and lines[0].strip().startswith('main_restrictors') and '[' in lines[0] and ']' in lines[0]:
        main_restrictors_line = lines[0].strip()
        data_start = 1
    else:
        data_start = 0

    # First pass: collect all key-value pairs
    kv_pairs = []
    comparator_name_value = None
    for line in lines[data_start:]:
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        kv_pairs.append((key, value))
        if key.lower() == 'comparator-name':
            comparator_name_value = value

    # Check for special case: only one comparator-name value and it is a form of Vehicle
    ignore_comparator_fields = set()
    if comparator_name_value:
        # Split by // and strip
        values = [v.strip() for v in comparator_name_value.split('//') if v.strip()]
        import re
        if len(values) == 1 and re.search(r'vehicle', values[0], re.IGNORECASE):
            ignore_comparator_fields = {'comparator-dosage', 'comparator-frequency'}

    import re
    for key, value in kv_pairs:
        # If value is empty and key is in ignore_comparator_fields, skip
        if key in ignore_comparator_fields and value == '':
            continue
        # If value is a restrictor (e.g., ((...))), keep it
        if value.strip().startswith('((') and value.strip().endswith('))'):
            empty_indexes.append(key)
        # Otherwise, add if value is empty and not ignored
        elif value == '' and key not in ignore_comparator_fields:
            empty_indexes.append(key)

    with open(output_path, 'w', encoding='utf-8') as fout:
        if main_restrictors_line:
            fout.write(main_restrictors_line + '\n')
        for idx in empty_indexes:
            fout.write(idx + '\n')

def extract_empty_indexes_all(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for file in input_dir.glob("*.txt"):
        output_file = output_dir / file.name
        extract_empty_indexes_from_file(file, output_file)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract empty indexes from all parsed output tables and write to extracted remain indexes.")
    parser.add_argument('--input_dir', default='../storage/parsed_output_tables', help='Input directory path')
    parser.add_argument('--output_dir', default='../storage/extracted_remain_indexes', help='Output directory path')
    args = parser.parse_args()
    extract_empty_indexes_all(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
