"""
Parses the output mapping index files to selected section titles,
and writes each file's selected titles (one per line) to a new directory 'parsed_index_2'.
Reads input from 'storage/output_file_promt_ai/output_indexes2.txt'.
"""

import os

def main(input_file=None, output_dir=None):
    """
    Main function to parse the output file and write selected section titles
    to individual files in the output directory, one title per line.
    Args:
        input_file (str): Path to the input file. Defaults to standard location.
        output_dir (str): Path to the output directory. Defaults to standard location.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if input_file is None:
        input_file = os.path.join(base_dir, "storage/output_file_promt_ai/output_titles.txt")
    if output_dir is None:
        output_dir = os.path.join(base_dir, "storage/parsed_titles")
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line or not line.startswith(";"):
                continue
            parts = line.split(";")
            if len(parts) < 3:
                continue
            filename = parts[1].strip()
            titles = [p.strip() for p in parts[2:] if p.strip()]
            if not filename or not titles:
                continue
            # Ensure .txt suffix for output files
            if not filename.endswith('.txt'):
                filename += '.txt'
            out_path = os.path.join(output_dir, filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(titles) + "\n")

if __name__ == "__main__":
    main()