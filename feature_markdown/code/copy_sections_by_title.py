"""
Copy sections from markdown files to new markdown files, in the order specified by a list of titles for each file.
- Reads titles from parsed_titles/*.txt (one per line, in desired order)
- Reads the full markdown from storage/markdown/{basename}/{basename}.md
- For each title, finds the corresponding section and copies its content (excluding images and tables) to a new markdown file, preserving formatting.
- Output: storage/coyed_section_by_file/{basename}_selected_sections.md
"""
import re
from pathlib import Path

def read_titles(titles_path):
    with open(titles_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def read_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_sections(lines, titles, all_titles_set):
    from rapidfuzz import fuzz, process

    # Build a list of (line, idx) for all lines in the file
    all_lines_in_file = [(line.strip(), idx) for idx, line in enumerate(lines)]

    # Fuzzy match all titles, allow matches to any line
    from rapidfuzz import fuzz
    matches = []
    for title in titles:
        best_score = 0
        best_idx = None
        best_line = None
        for line, idx in all_lines_in_file:
            # Strip leading '#' and whitespace for header lines
            line_stripped = line.lstrip('#').strip()
            score = fuzz.ratio(title.lower(), line_stripped.lower())
            if score > best_score:
                best_score = score
                best_idx = idx
                best_line = line
        pass
        if best_score >= 92 and best_idx is not None:
            matches.append((title, best_idx, best_score, best_line))
        else:
            pass

    # Remove duplicate indices (keep first occurrence in titles order)
    seen_idxs = set()
    unique_matches = []
    for m in matches:
        if m[1] not in seen_idxs:
            unique_matches.append(m)
            seen_idxs.add(m[1])
        else:
            pass

    # Sort by matched index in file order
    unique_matches.sort(key=lambda x: x[1])

    # Build sections: each section goes from its matched idx to the next markdown header (or next matched idx, whichever comes first)
    header_pattern = re.compile(r'^\s*#{1,6}[^#]')
    sections = []
    for i, (title, start_idx, score, matched_line) in enumerate(unique_matches):
        # Find the next header after start_idx
        next_header_idx = None
        for j in range(start_idx + 1, len(lines)):
            if header_pattern.match(lines[j]):
                next_header_idx = j
                break
        # Also consider the next matched title index
        if i < len(unique_matches) - 1:
            next_title_idx = unique_matches[i+1][1]
        else:
            next_title_idx = len(lines)
        # Section ends at the earliest of next header or next matched title
        if next_header_idx is not None:
            end_idx = min(next_header_idx, next_title_idx)
        else:
            end_idx = next_title_idx
        pass
        sections.append((title, start_idx, end_idx))
    pass
    return sections

def is_table_line(line):
    # Simple check for markdown tables: header or separator or row
    line = line.strip()
    if line.startswith("|") and line.endswith("|"):
        return True
    if re.match(r'^\s*\|?(\s*-+\s*\|)+\s*$', line):
        return True
    return False

def write_sections(lines, sections, output_path, all_titles_set):
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, (title, start, end) in enumerate(sections):
            # Write the title line
            f.write(lines[start])
            # Write lines until the next recognized title (from all_titles_set), or until 'end'
            for i in range(start+1, end):
                line = lines[i]
                if line.strip() in all_titles_set:
                    break
                if re.match(r'!\[.*\]\(.*\)', line.strip()):
                    continue
                if is_table_line(line):
                    continue
                f.write(line)
            # Add a blank line only between sections, not after every line
            if idx < len(sections) - 1:
                f.write('\n')


def process_all_files(titles_dir=None, markdown_dir=None, output_dir=None, all_titles_dir=None):
    base_dir = Path(__file__).parent.parent
    # Ensure all input/output directories are Path objects
    if titles_dir is None:
        titles_dir = base_dir / "storage" / "parsed_titles"
    else:
        titles_dir = Path(titles_dir)
    if markdown_dir is None:
        markdown_dir = base_dir / "storage" / "markdown"
    else:
        markdown_dir = Path(markdown_dir)
    if output_dir is None:
        output_dir = base_dir / "storage" / "coyed_section_by_file"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # New: get all_titles_dir from input or default
    if all_titles_dir is None:
        all_titles_dir = titles_dir
    else:
        all_titles_dir = Path(all_titles_dir)
    # Build all_titles_set from all_titles_dir
    all_titles_set = set()
    for tfile in all_titles_dir.glob("*.txt"):
        with open(tfile, 'r', encoding='utf-8') as tf:
            for tline in tf:
                t = tline.strip()
                if t:
                    all_titles_set.add(t)

    processed = 0
    skipped = 0
    found_files = list(titles_dir.glob("*.txt"))
    for titles_path in found_files:
        basename = titles_path.stem  # e.g. "Bissonnette 2016"
        md_path = markdown_dir / basename / f"{basename}.md"
        if not md_path.exists():
            skipped += 1
            continue
        output_path = output_dir / f"{basename}_selected_sections.md"
        titles = read_titles(titles_path)
        if not titles:
            skipped += 1
            continue
        lines = read_markdown(md_path)
        if not lines:
            skipped += 1
            continue
        sections = find_sections(lines, titles, all_titles_set)
        if not sections:
            skipped += 1
        else:
            processed += 1
        write_sections(lines, sections, output_path, all_titles_set)

def main():
    process_all_files()

if __name__ == "__main__":
    main()
