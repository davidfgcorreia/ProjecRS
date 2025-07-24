# This script will copy all tables (and their titles, if present) from all markdown files in the input directory
# and return a single markdown file with all tables concatenated, preserving their original formatting.

import os
import re


def load_markdown_files(md_dir):
    """
    Loads all markdown files from the given directory and its subdirectories.
    Returns a dict: filename -> content (as string)
    """
    data = {}
    for root, dirs, files in os.walk(md_dir):
        for fname in files:
            if fname.lower().endswith('.md'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    data[fpath] = f.read()
    return data


def copy_all_tables_to_single_md(md_dir, output_md_path, debug=False):
    data = load_markdown_files(md_dir)
    all_tables = []
    for fname, content in data.items():
        lines = content.splitlines()
        i = 0
        while i < len(lines):
            # Identify a table: at least two pipes and not just dashes/spaces
            if lines[i].count('|') >= 2 and not all(c in '-| ' for c in lines[i]):
                table_block = []
                # Optionally include the table title if present (line above with 'Table')
                title_idx = i - 1 if i > 0 and 'Table' in lines[i-1] else None
                # If title is present, check for description between title and table
                if title_idx is not None:
                    table_block.append(lines[title_idx])
                    # Look for description lines between title and table (non-empty, not a table, not just dashes)
                    desc_lines = []
                    j = title_idx + 1
                    while j < i:
                        if lines[j].strip() and not (lines[j].count('|') >= 2 or all(c in '-| ' for c in lines[j])):
                            desc_lines.append(lines[j])
                        j += 1
                    if desc_lines:
                        table_block.extend(desc_lines)
                # If no title, check for description above the table (up to 2 lines above, not empty, not a table, not just dashes)
                elif i > 0:
                    desc_lines = []
                    j = i - 1
                    total_words_before = 0
                    while j >= max(0, i - 2):
                        if lines[j].strip() and not (lines[j].count('|') >= 2 or all(c in '-| ' for c in lines[j])):
                            line_words = lines[j].split()
                            if total_words_before + len(line_words) > 20:
                                words_left = 20 - total_words_before
                                if words_left > 0:
                                    desc_lines.insert(0, ' '.join(line_words[:words_left]))
                                    total_words_before += words_left
                                break
                            else:
                                desc_lines.insert(0, lines[j])
                                total_words_before += len(line_words)
                        j -= 1
                    if desc_lines:
                        table_block.extend(desc_lines)
                # Copy all consecutive lines with at least two pipes
                table_start = i
                while i < len(lines) and lines[i].count('|') >= 2:
                    table_block.append(lines[i])
                    i += 1
                # Also copy the next 5 lines after the table (footnotes, abbreviations, etc.), but stop if >30 words
                post_table_lines = []
                word_count = 0
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip():
                        line_word_count = len(lines[j].split())
                        if word_count + line_word_count > 30:
                            # Only add up to the remaining words
                            words_left = 30 - word_count
                            if words_left > 0:
                                truncated_line = ' '.join(lines[j].split()[:words_left])
                                post_table_lines.append(truncated_line)
                                word_count += words_left
                            break
                        else:
                            post_table_lines.append(lines[j])
                            word_count += line_word_count
                    if word_count >= 30:
                        break
                if post_table_lines:
                    table_block.extend(post_table_lines)
                all_tables.append('\n'.join(table_block))
            else:
                i += 1
    with open(output_md_path, 'w', encoding='utf-8') as f:
        for t in all_tables:
            f.write(t + '\n\n')
    if debug:
        print(f"Wrote all tables to {output_md_path}")

def process_all_subfolders(md_root, output_root, debug=False):
    """
    For each subfolder in md_root, run copy_all_tables_to_single_md and output to output_root/<subfolder>_tables.md
    """
    for subfolder in os.listdir(md_root):
        subfolder_path = os.path.join(md_root, subfolder)
        if os.path.isdir(subfolder_path):
            output_md_path = os.path.join(output_root, f'{subfolder}_tables.md')
            if debug:
                print(f"Processing {subfolder_path} -> {output_md_path}")
            copy_all_tables_to_single_md(subfolder_path, output_md_path, debug=debug)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Copy all tables from each subfolder of markdown into separate output folders.")
    parser.add_argument('--md_root', default='../storage/markdown', help='Root directory with marker-generated markdown subfolders')
    parser.add_argument('--output_root', default='../storage/tables', help='Root directory to store output subfolders')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    process_all_subfolders(args.md_root, args.output_root, debug=args.debug)

if __name__ == "__main__":
    main()
