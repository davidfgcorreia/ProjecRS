"""
Script to extract all document titles (markdown headers) from markdown file(s) and write them to a .txt file, one title per line.
A title is only included if it is followed by at least two lines of non-title (non-header) text before the next title.
This ensures that only titles with substantial readable content are included.

Usage:
    python extract_titles.py

- All .md files in the markdown directory will be processed.
- Titles are lines starting with one or more '#' (markdown headers).
- Output files are placed in the pdfs_titles directory.
"""
import os
import glob

DEFAULT_INPUT_DIR = "/root/documnetos/Estagio/projeto/feature_markdown/storage/markdown"
DEFAULT_OUTPUT_DIR = "/root/documnetos/Estagio/projeto/feature_markdown/storage/pdfs_titles"

def extract_titles_with_content(input_dir=DEFAULT_INPUT_DIR, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Extracts all markdown titles (headers) from all .md files in input_dir and writes them to .txt files in output_dir.
    A title is only included if it is followed by at least two lines of non-title (non-header) text before the next title.
    Titles are not deduplicated and are written in the order found.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    md_files = glob.glob(os.path.join(input_dir, '**', '*.md'), recursive=True)
    import re
    for md_file in md_files:
        titles = []
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        n = len(lines)
        i = 0
        while i < n:
            line = lines[i].strip()
            # Candidate title: markdown header or any line with 1-4 words
            is_header = line.startswith('#')
            candidate_title = None
            if is_header:
                candidate_title = line.lstrip('#').strip()
            elif line and 1 <= len(line.split()) <= 4:
                candidate_title = line
            if candidate_title:
                # Look ahead for at least 2 lines of non-title, non-empty text
                content_lines = []
                j = i + 1
                while j < n:
                    next_line = lines[j].strip()
                    next_is_title = next_line.startswith('#') or (next_line and 1 <= len(next_line.split()) <= 4)
                    if next_is_title:
                        break
                    if next_line != '':
                        content_lines.append(next_line)
                    j += 1
                if len(content_lines) >= 2:
                    titles.append(candidate_title)
                i = j
            else:
                i += 1
        # Classical title heuristics: filter out trash titles
        filtered_titles = []
        for title in titles:
            # Must start with uppercase letter
            if not title or not title[0].isupper():
                continue
            # Not all lowercase
            if title.islower():
                continue
            # Not only numbers or symbols
            if all(not c.isalpha() for c in title):
                continue
            # Not too short (e.g., 1 character)
            if len(title) < 2:
                continue

            filtered_titles.append(title)
        # Output file name
        base = os.path.splitext(os.path.basename(md_file))[0]
        out_path = os.path.join(output_dir, f"{base}_titles.txt")
        with open(out_path, 'w', encoding='utf-8') as out_f:
            for title in filtered_titles:
                out_f.write(title + '\n')

def main():
    extract_titles_with_content()

if __name__ == "__main__":
    main()
