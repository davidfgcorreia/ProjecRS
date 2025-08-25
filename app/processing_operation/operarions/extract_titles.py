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
import re

def extract_titles_with_content(input_dir, output_dir):
    """
    Extracts all candidate titles from markdown files:
    - Any line starting with '#' is a candidate title.
    - If two candidate titles are consecutive, only include the second.
    - Exclude weird titles: images, tables, DOIs, numbers, very short, or only symbols.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    md_files = glob.glob(os.path.join(input_dir, '**', '*.md'), recursive=True)
    for md_file in md_files:
        titles = []
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        n = len(lines)
        prev_was_title = False
        i = 0
        while i < n:
            line = lines[i].strip()
            is_hash_title = line.startswith('#')
            is_heuristic_title = False
            if not is_hash_title:
                if (2 <= len(line) <= 80 and
                    not line.islower() and
                    any(c.isalpha() for c in line) and
                    not re.match(r'^\d+$', line) and
                    not re.match(r'^DOI', line, re.IGNORECASE) and
                    not re.match(r'^!\[.*\]\(.*\)$', line) and
                    not re.match(r'^\|', line) and
                    not re.match(r'^[^A-Za-z0-9]+$', line) and
                    len(line.split()) <= 8):
                    is_heuristic_title = True
            skip_main_title = False
            if is_hash_title:
                j = i + 1
                segment_titles = []
                while j < n and lines[j].strip() == '':
                    j += 1
                    if j >= n:
                        break
                while j < n:
                    next_line = lines[j].strip()
                    next_is_hash_title = next_line.startswith('#')
                    next_is_heuristic_title = False
                    if not next_is_hash_title:
                        if (2 <= len(next_line) <= 80 and
                            not next_line.islower() and
                            any(c.isalpha() for c in next_line) and
                            not re.match(r'^\d+$', next_line) and
                            not re.match(r'^DOI', next_line, re.IGNORECASE) and
                            not re.match(r'^!\[.*\]\(.*\)$', next_line) and
                            not re.match(r'^\|', next_line) and
                            not re.match(r'^[^A-Za-z0-9]+$', next_line) and
                            len(next_line.split()) <= 8):
                            next_is_heuristic_title = True
                    if next_is_hash_title or next_is_heuristic_title:
                        segment_titles.append(next_line)
                        j += 1
                        while j < n and lines[j].strip() == '':
                            j += 1
                            if j >= n:
                                break
                        if j >= n:
                            break
                    else:
                        break
                if len(segment_titles) > 0:
                    i = j
                    prev_was_title = False
                    continue
            if (is_hash_title or is_heuristic_title) and not skip_main_title:
                title = re.sub(r'[*_`#]', '', line).strip()
                if not title or len(title) < 2:
                    prev_was_title = True
                    i += 1
                    continue
                if len(title.split()) > 20:
                    prev_was_title = True
                    i += 1
                    continue
                if title.islower() or (all(not c.isalpha() for c in title) and not any(c.isupper() for c in title)):
                    prev_was_title = True
                    i += 1
                    continue
                if re.match(r'^\d+$', title) or (len(title.split()) < 2 and not is_hash_title):
                    prev_was_title = True
                    i += 1
                    continue
                if (re.match(r'^DOI', title, re.IGNORECASE) or
                    re.match(r'^!\[.*\]\(.*\)$', title) or
                    re.search(r'<(div|span|sup|img|table|figure)[^>]*>', title) or
                    re.match(r'^\|', title) or
                    re.match(r'^[^A-Za-z0-9]+$', title) or
                    re.match(r'^(Figure|Table)\s*\d+\.', title) or
                    re.match(r'^<sup>.*</sup>', title) or
                    title.startswith('!') or title.startswith('span') or title.startswith('<span')):
                    prev_was_title = True
                    i += 1
                    continue
                if re.search(r'(Table|Image|[Ff][Ii][Gg][Uu][Rr][Ee]|[Ff][Ii][Gg])([ ._\d]*)', title):
                    prev_was_title = True
                    i += 1
                    continue
                if sum(1 for c in title if not c.isalnum() and not c.isspace()) > len(title) // 2:
                    prev_was_title = True
                    i += 1
                    continue
                if prev_was_title:
                    prev_was_title = False
                    i += 1
                    continue
                titles.append(title)
                prev_was_title = True
                i += 1
            else:
                prev_was_title = False
                i += 1
        base = os.path.splitext(os.path.basename(md_file))[0]
        out_path = os.path.join(output_dir, f"{base}_titles.txt")
        with open(out_path, 'w', encoding='utf-8') as out_f:
            for title in titles:
                out_f.write(title + '\n')

def main():
    extract_titles_with_content(input_dir="../storage/markdown", output_dir="../storage/pdfs_titles")

if __name__ == "__main__":
    main()
