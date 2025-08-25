"""
Parse LLM output/inspection files to structured intermediate formats.

Used to read text outputs produced by LLM prompts and transform them into
structured index files for downstream parsing.
"""
import re
from pathlib import Path

def fix_bracket_format(line):
    # Split at the first colon
    if ':' not in line:
        return line
    key, value = line.split(':', 1)
    value = value.lstrip()
    # Only fix if value starts with a single bracket (not already double)
    # and not empty
    def replace_first_bracket_block(val):
        # Only replace the first occurrence at the start or after //
        def _repl(m):
            inner = m.group(1)
            # If already double-bracketed, skip
            if inner.startswith('(') and inner.endswith(')'):
                return m.group(0)
            return f'(({inner}))'
        # Replace only the first single-bracket block at the start
        return re.sub(r'^\(([^()]+)\)', _repl, val, count=1)
    # Also fix after each //
    parts = value.split('//')
    fixed_parts = [replace_first_bracket_block(p.strip()) for p in parts]
    fixed_value = ' // '.join(fixed_parts)
    return f'{key}: {fixed_value}\n'

def review_and_fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    changed = False
    new_lines = []
    for line in lines:
        if re.search(r':\s*\([^)]*\)', line):
            # Only fix if not already double brackets
            if not re.search(r':\s*\(\([^)]*\)\)', line):
                fixed = fix_bracket_format(line)
                if fixed != line:
                    changed = True
                new_lines.append(fixed)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"File {file_path} was fixed and rewritten.")
    else:
        print(f"File {file_path} is already in correct format.")

def main():
    # Review all .txt files in parsed_output_tables directory
    dir_path = Path('../storage/parsed_output_tables')
    for file_path in dir_path.glob('*.txt'):
        review_and_fix_file(file_path)

if __name__ == "__main__":
    main()
