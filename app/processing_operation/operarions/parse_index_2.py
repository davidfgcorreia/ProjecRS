"""Parser for the second index format produced by earlier pipeline steps.

Provides utilities to read the `ouput_indexs.txt` style files and write
structured parsed outputs to a target directory.
"""

import os
import re

def parse_and_write(input_file=None, output_dir=None):
    if input_file is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(BASE_DIR, "../storage/output_file_promt_ai/output_indexes2.txt")
    if output_dir is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(BASE_DIR, "../storage/parsed_index_2")
    os.makedirs(output_dir, exist_ok=True)
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line or ";" not in line:
                continue
            match = re.match(r"^([^\[\];]+)\s*(\[[^]]*\])?\s*;\s*(.*)$", line)
            if not match:
                continue
            base = match.group(1).strip()
            restrictors = match.group(2)
            rest = match.group(3).strip()
            # Split on semicolons not inside curly braces
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
                    if c == ';' and depth == 0:
                        segments.append(''.join(current).strip())
                        current = []
                    else:
                        current.append(c)
                if current:
                    segments.append(''.join(current).strip())
                return [seg for seg in segments if seg]
            segments = split_outside_curly(rest)
            output_path = os.path.join(output_dir, f"{base}.txt")
            parsed_lines = []
            if restrictors:
                restrictors = restrictors.strip()
                parsed_lines.append(f"main_restrictors : {restrictors}")
            parsed_lines.extend(segments)
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n".join(parsed_lines) + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        parse_and_write(sys.argv[1], sys.argv[2])
    else:
        parse_and_write()