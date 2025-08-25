"""Copy selected sections from markdown files based on title lists.

This module provides utilities to read ordered title lists and extract the
matching sections from markdown documents, producing per-file markdowns with
only the chosen sections.

Main functions:
- read_titles(path) -> list[str]
- read_markdown(path) -> list[str]
- find_sections(lines, titles, all_titles_set, pdf_titles=None) -> list[(title,start,end)]
"""


import re
from pathlib import Path
from rapidfuzz import fuzz

def read_titles(titles_path):
    with open(titles_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def read_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_sections(lines, titles, all_titles_set, pdf_titles=None):
    # If pdf_titles is provided, use it as delimiters
    if pdf_titles is not None:
        title_indices = []
        for title in pdf_titles:
            best_score = 0
            best_idx = None
            for idx, line in enumerate(lines):
                line_stripped = line.lstrip('#').strip()
                score = fuzz.ratio(title.lower(), line_stripped.lower())
                if score > best_score:
                    best_score = score
                    best_idx = idx
            if best_score >= 92 and best_idx is not None:
                title_indices.append((title, best_idx))
            else:
                title_indices.append((title, None))
        sections = []
        for i, (title, start_idx) in enumerate(title_indices):
            if start_idx is None:
                continue
            if i < len(title_indices) - 1:
                next_found = None
                for j in range(i+1, len(title_indices)):
                    if title_indices[j][1] is not None:
                        next_found = title_indices[j][1]
                        break
                end_idx = next_found if next_found is not None else len(lines)
            else:
                end_idx = len(lines)
            sections.append((title, start_idx, end_idx))
        return sections

    # Build a list of (line, idx) for all lines in the file
    all_lines_in_file = [(line.strip(), idx) for idx, line in enumerate(lines)]

    # Fuzzy match all titles, allow matches to any line
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
    # All input/output directories must be provided as arguments (no hardcoded defaults)
    if titles_dir is None or markdown_dir is None or output_dir is None or all_titles_dir is None:
        raise ValueError("All directory arguments must be provided explicitly. No hardcoded defaults allowed.")

    # Ensure all input/output directories are Path objects
    titles_dir = Path(titles_dir)
    markdown_dir = Path(markdown_dir)
    output_dir = Path(output_dir)
    all_titles_dir = Path(all_titles_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build all_titles_set from all_titles_dir
    all_titles_set = set()
    for tfile in all_titles_dir.glob("*.txt"):
        with open(tfile, 'r', encoding='utf-8') as tf:
            for tline in tf:
                t = tline.strip()
                if t:
                    all_titles_set.add(t)

    found_files = list(titles_dir.glob("*.txt"))
    for titles_path in found_files:
        basename = titles_path.stem  # e.g. "Bissonnette 2016"
        md_path = markdown_dir / basename / f"{basename}.md"
        pdf_titles_path = all_titles_dir / f"{basename}_titles.txt"
        if not md_path.exists() or not pdf_titles_path.exists():
            continue
        output_path = output_dir / f"{basename}_selected_sections.md"
        titles = read_titles(titles_path)
        pdf_titles = read_titles(pdf_titles_path)
        lines = read_markdown(md_path)
        sections = find_sections(lines, titles, all_titles_set, pdf_titles=pdf_titles)
        # Filter sections to only those whose title is in the selected titles list
        selected_titles_set = set(titles)
        filtered_sections = [s for s in sections if s[0] in selected_titles_set]
        write_sections(lines, filtered_sections, output_path, all_titles_set)

def main():
    raise NotImplementedError("You must call process_all_files with explicit directory arguments. No hardcoded defaults.")

if __name__ == "__main__":
    main()
