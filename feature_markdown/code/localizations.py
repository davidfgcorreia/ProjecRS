import re
import json
from pathlib import Path


def extract_and_replace_localizations(input_path, output_path, id_prefix, id_start=1):
    """
    Processes a key-value file, extracts localizations, replaces them with @@id@@, and writes cleaned file.
    Returns a dict: {unique_id: {"key": key, "localization": localization}}
    """
    localizations = {}
    id_counter = id_start
    output_lines = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            orig_line = line
            line = line.strip()
            if not line or ':' not in line:
                output_lines.append(orig_line.rstrip())
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Split on //, but not inside braces
            def split_outside_curly(s):
                segments = []
                current = []
                depth = 0
                for c in s:
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        if depth > 0:
                            depth -= 1
                    if c == '/' and depth == 0:
                        if current and current[-1] == '/':
                            segments.append(''.join(current[:-1]).strip())
                            current = []
                        else:
                            current.append(c)
                    else:
                        current.append(c)
                if current:
                    segments.append(''.join(current).strip())
                return [seg for seg in segments if seg]
            parts = split_outside_curly(value)
            new_parts = []
            for part in parts:
                val = part
                loc = None
                start = val.find('{')
                if start != -1:
                    depth = 0
                    loc_start = None
                    for i in range(start, len(val)):
                        if val[i] == '{':
                            if depth == 0:
                                loc_start = i
                            depth += 1
                        elif val[i] == '}':
                            depth -= 1
                            if depth == 0 and loc_start is not None:
                                loc = val[loc_start+1:i]
                                val = val[:loc_start].strip()
                                break
                    else:
                        if loc_start is not None:
                            loc = val[loc_start+1:].strip()
                            val = val[:loc_start].strip()
                if loc:
                    unique_id = f"{id_prefix}{id_counter}"
                    localizations[unique_id] = {"key": key, "localization": loc}
                    new_parts.append(f"{val} @@{unique_id}@@" if val else f"@@{unique_id}@@")
                    id_counter += 1
                else:
                    new_parts.append(val)
            new_value = ' // '.join([p for p in new_parts if p])
            output_lines.append(f"{key}: {new_value}".rstrip())
    with open(output_path, 'w', encoding='utf-8') as f:
        for l in output_lines:
            f.write(l + '\n')
    return localizations, id_counter


def process_and_save_all(input_dir, output_dir, loc_json_path):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_localizations = {}
    id_counter = 1
    for file in input_dir.glob('*.txt'):
        out_file = output_dir / file.name
        file_locs, id_counter = extract_and_replace_localizations(
            file, out_file, id_prefix="loc_", id_start=id_counter)
        for k, v in file_locs.items():
            v['file'] = str(file.name)
        all_localizations.update(file_locs)
    with open(loc_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_localizations, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        process_and_save_all(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Example usage
        process_and_save_all(
            '../main_storage/exemple2/final_values_for_tables',
            '../main_storage/exemple2/final_values_whit_ids',
            '../main_storage/exemple2/localizations/localizations_map.json')
