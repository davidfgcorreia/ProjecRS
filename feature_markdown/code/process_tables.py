import os
import re
import requests
from typing import List, Tuple, Optional

def extract_compounds(row: str) -> List[str]:
    """
    Extracts compound acronyms from a markdown table row using regex.
    Returns a list of acronyms.
    """
    return re.findall(r'\b[A-Z]{2,}(?:-\d{2,})?\b', row)

def extract_dosage(dosage: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts percentage and frequency (b.i.d., q.d., etc.) from dosage string.
    Returns a tuple (percentage, frequency).
    """
    percent = re.search(r'(\d+(\.\d+)?%)', dosage)
    # Normalize frequency synonyms to standard abbreviations
    freq_map = {
        'once daily': 'q.d.',
        'twice daily': 'b.i.d.',
        'three times daily': 't.i.d.',
        'four times daily': 'q.i.d.',
        'b.i.d.': 'b.i.d.',
        'bid': 'b.i.d.',
        'q.d.': 'q.d.',
        'qd': 'q.d.',
        't.i.d.': 't.i.d.',
        'tid': 't.i.d.',
        'q.i.d.': 'q.i.d.',
        'qid': 'q.i.d.'
    }
    # Find all frequency notations in the string (with or without trailing dot)
    freq_matches = re.findall(r'\b(b\.i\.d\.?|bid|q\.d\.?|qd|t\.i\.d\.?|tid|q\.i\.d\.?|qid|once daily|twice daily|three times daily|four times daily)\b', dosage, re.IGNORECASE)
    norm_freqs = []
    for f in freq_matches:
        f_lc = f.lower().replace(' ', '')
        for k, v in freq_map.items():
            if f_lc == k.replace(' ', '').replace('.', ''):
                norm_freqs.append(v)
                break
        else:
            norm_freqs.append(f)
    percent_val = percent.group(1) if percent else None
    freq_val = ' '.join(norm_freqs) if norm_freqs else None
    return (percent_val, freq_val)

def fix_comparator(name: str) -> str:
    """
    Adds 'ointment' after 'Vehicle' in comparator names using regex.
    """
    if re.match(r'(?i)^vehicle$', name.strip()):
        return f"{name.strip()} ointment"
    return name.strip()

def process_markdown_table(md_path: str, out_path: str) -> None:
    """
    Processes a markdown table file:
    - Extracts compound acronyms using regex
    - Cleans dosages to keep only percentage and frequency
    - Adds 'ointment' after 'Vehicle' in comparator names
    - Outputs a new markdown table
    """
    # Read markdown table
    with open(md_path, 'r') as f:
        lines = f.readlines()
    # Find table lines
    table_lines = [line for line in lines if line.strip().startswith('|')]
    if not table_lines:
        raise ValueError('No markdown table found.')
    # Parse header
    header = table_lines[0].strip().split('|')[1:-1]
    # Parse rows
    rows = [l.strip().split('|')[1:-1] for l in table_lines[2:]]
    # Helper: get full compound name from PubChem, prefer simple names (not formula/IUPAC)
    def get_full_name(acronym: str) -> str:
        def is_simple_name(name):
            words = [w for w in re.split(r'\s+', name.strip()) if w]
            if not (1 <= len(words) <= 4):
                return False
            for w in words:
                if len(w) > 20:
                    return False
                if any(c in w for c in [',', '~', '{', '}', '(', ')']):
                    return False
                if w.count('-') > 2:
                    return False
                if not re.match(r'^[\w\-]+$', w):
                    return False
            return True

        url_pubchem = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{acronym}/synonyms/JSON"
        try:
            resp = requests.get(url_pubchem, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                synonyms = data['InformationList']['Information'][0].get('Synonym', [])
                if synonyms:
                    synonym = synonyms[0]
                    if is_simple_name(synonym):
                        return synonym
        except Exception:
            pass
        return acronym
    # Indices for relevant columns using regex
    def find_col_idx(header: List[str], pattern: str) -> Optional[int]:
        for i, col in enumerate(header):
            if re.search(pattern, col, re.IGNORECASE):
                return i
        return None

    idx_name = find_col_idx(header, r'name')
    idx_dosage = find_col_idx(header, r'dosage')
    idx_comp = find_col_idx(header, r'comp')
    # Match columns named 'age', 'intervention-age', '-age', 'age-', etc. (case-insensitive, with hyphen before or after)
    idx_age = None
    for i, col in enumerate(header):
        col_clean = col.strip().lower()
        if (
            col_clean == 'age' or
            col_clean == 'intervention-age' or
            col_clean.endswith('-age') or
            col_clean.startswith('age-')
        ):
            idx_age = i
            break
    if idx_name is None or idx_dosage is None or idx_comp is None:
        raise ValueError('Required columns not found in table header.')
    # Age column is optional, but if present, normalize it
    # Process rows
    new_rows = []
    def normalize_age(age_str: str) -> str:
        """
        Normalize age string to 'median (min-max)' format.
        Handles:
        - mean ± std: '29.5 ± 9.2' -> '29.5 (20.3-38.7)'
        - median (IQR): '8.5 (4.4)' -> '8.5 (6.3-10.7)'
        - median (min-max): keep as is
        - single value: '30' -> '30 (30-30)'
        Removes units.
        """
        if not age_str or not isinstance(age_str, str):
            return ''
        s = age_str.strip()
        s = re.sub(r'\b(years?|yrs?|yo|y/o|y)\b', '', s, flags=re.IGNORECASE).strip()
        match_pm = re.search(r'([\d.]+)\s*[±\+\-]\s*([\d.]+)', s)
        if match_pm:
            mean = float(match_pm.group(1))
            std = float(match_pm.group(2))
            min_age = round(mean - std, 1)
            max_age = round(mean + std, 1)
            return f"{mean} ({min_age}-{max_age})"
        match_paren = re.search(r'([\d.]+)\s*\(\s*([^)]+?)\s*\)', s)
        if match_paren:
            median = float(match_paren.group(1))
            inner = match_paren.group(2)
            range_match = re.search(r'([\d.]+)\s*-\s*([\d.]+)', inner)
            if range_match:
                min_age = float(range_match.group(1))
                max_age = float(range_match.group(2))
                return f"{median} ({min_age}-{max_age})"
            try:
                iqr = float(inner)
                min_age = round(median - iqr/2, 1)
                max_age = round(median + iqr/2, 1)
                return f"{median} ({min_age}-{max_age})"
            except Exception:
                pass
        match_force = re.search(r'([\d.]+)\s*\(\s*([\d.]+)\s*-\s*([\d.]+)\s*\)', s)
        if match_force:
            median = float(match_force.group(1))
            min_age = float(match_force.group(2))
            max_age = float(match_force.group(3))
            return f"{median} ({min_age}-{max_age})"
        match_single = re.search(r'^([\d.]+)$', s)
        if match_single:
            val = float(match_single.group(1))
            return f"{val} ({val}-{val})"
        return f"{s}"

    for row in rows:
        # intervention-name: expand only the first connected word (acronym)
        compounds = extract_compounds(row[idx_name])
        if compounds:
            first_acronym = compounds[0]
            full_name = get_full_name(first_acronym)
            row[idx_name] = full_name
        # intervention-dosage: clean dosage
        percent, freq = extract_dosage(row[idx_dosage])
        # Always preserve frequency notation if present, even if percent is missing
        if percent or freq:
            parts = []
            if percent:
                parts.append(percent)
            if freq:
                parts.append(freq)
            row[idx_dosage] = ' '.join(parts)
        else:
            row[idx_dosage] = row[idx_dosage]
        # frequency column: normalize if present
        freq_col_idxs = [i for i, col in enumerate(header) if re.search(r'frequency', col, re.IGNORECASE)]
        for freq_idx in freq_col_idxs:
            if freq_idx < len(row):
                # Normalize frequency in this column
                _, norm_freq = extract_dosage(row[freq_idx])
                if norm_freq:
                    row[freq_idx] = norm_freq
        # comparator-name: fix comparator
        row[idx_comp] = fix_comparator(row[idx_comp])
        # age: normalize if present
        if idx_age is not None and idx_age < len(row):
            row[idx_age] = normalize_age(row[idx_age])
        new_rows.append(row)

    # Capitalize only the first letter of each cell in all columns (header and rows),
    # but do NOT capitalize frequency columns (e.g., those with 'frequency' in the header)
    def cap_first_alpha(s):
        if not isinstance(s, str) or not s:
            return str(s)
        for i, c in enumerate(s):
            if c.isalpha():
                return s[:i] + c.upper() + s[i+1:]
        return s

    # Identify frequency columns
    freq_col_idxs = [i for i, col in enumerate(header) if re.search(r'frequency', col, re.IGNORECASE)]
    capitalized_header = [cap_first_alpha(col) for col in header]
    with open(out_path, 'w') as f:
        f.write('| ' + ' | '.join(capitalized_header) + ' |\n')
        f.write('|' + '|'.join(['---'] * len(header)) + '|\n')
        for row in new_rows:
            capitalized_row = [
                (x if i in freq_col_idxs else cap_first_alpha(x))
                for i, x in enumerate(row)
            ]
            f.write('| ' + ' | '.join(capitalized_row) + ' |\n')



def main(input_dir=None, output_dir=None):
    import sys
    # Accept input_dir and output_dir as arguments or CLI
    if input_dir is None or output_dir is None:
        if len(sys.argv) >= 3:
            input_dir = sys.argv[1]
            output_dir = sys.argv[2]
        else:
            input_dir = "../storage/final_values_for_table"
            output_dir = "../storage/final_values_for_table"
    input_path = os.path.join(input_dir, "all_tables_merged.md")
    output_path = os.path.join(output_dir, "all_tables_processed.md")
    process_markdown_table(input_path, output_path)
    print(f"Processed table written to {output_path}")

if __name__ == "__main__":
    main()