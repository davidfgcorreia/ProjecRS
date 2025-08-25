"""Find a section in a markdown document using explicit markers.

Simple helper to locate a block delimited by marker strings or header
patterns. Useful for deterministic section extraction when markers exist.
"""

# Standard library imports
import re
import os
import sys
import html
from pathlib import Path
from typing import Optional

# Third-party imports
import fitz

def normalize(text):
    if not text:
        return ''
    text = html.unescape(text)
    # Replace HTML tags and <br> with a space
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Replace markdown formatting: *, _, #, `, >, -, +, ~, !, |, etc. with a space (do NOT remove [] () or =)
    text = re.sub(r'[\*_#`>\-\+~!|]', ' ', text)
    # Collapse multiple spaces to one
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def extract_sections_with_marker(pdf_path: str, marker: str, localization_value: Optional[str] = None, output_path: Optional[str] = None):
    print(f"[DEBUG] Called extract_sections_with_marker with pdf_path={pdf_path}, marker={marker}, localization_value={localization_value}")
    """
    normalizes localization value to current format without html tags and other formatting.
    finds the section on the original markdown file
    finds the section on the original pdf
    copies the section to a new pdf file (using the markdown json file)
    highlights the marker in the new pdf
    make hyperlink to the highlighted marker in the output pdf and place them in the beginning of the output pdf
    has no return value, but writes the output pdf to the output path
    """

    # 2. Use PyMuPDF's search_for to find the best substring match in the PDF
    print(f"[DEBUG] Searching entire PDF for best substring matches of localization value: {localization_value}")

    doc = fitz.open(pdf_path) 
    if not localization_value:
        print("[WARN] No localization value provided for PDF search.")
        return
    search_string = localization_value.strip()
    words = [normalize(word) for word in search_string.split()]
    # Try both strategies and pick the best
    matches_remove_last = []
    maxlen_last = 0
    for substr_len in range(len(words), 0, -1):
        substr = ' '.join(words[:substr_len])
        print(f"[DEBUG] Searching for substring (removing last): '{substr}'")
        found_any = False
        for page_num in range(doc.page_count):
            page = doc[page_num]
            rects = page.search_for(substr)  # type: ignore[reportAttributeAccessIssue]
            for rect in rects:
                found_any = True
                matches_remove_last.append({'page': page_num, 'rect': rect, 'text': substr, 'length': substr_len})
        if found_any and substr_len > maxlen_last:
            maxlen_last = substr_len
    # Remove first
    matches_remove_first = []
    maxlen_first = 0
    for start in range(1, len(words)+1):
        substr = ' '.join(words[start-1:])
        if not substr:
            continue
        print(f"[DEBUG] Searching for substring (removing first): '{substr}'")
        found_any = False
        for page_num in range(doc.page_count):
            page = doc[page_num]
            rects = page.search_for(substr)  # type: ignore[reportAttributeAccessIssue]
            for rect in rects:
                found_any = True
                matches_remove_first.append({'page': page_num, 'rect': rect, 'text': substr, 'length': len(substr.split())})
        if found_any and len(substr.split()) > maxlen_first:
            maxlen_first = len(substr.split())
    # Pick the best: prefer longest match, then most matches
    best_matches = []
    best_length = 0
    if maxlen_last > maxlen_first:
        best_matches = [m for m in matches_remove_last if m['length'] == maxlen_last]
        best_length = maxlen_last
        print(f"[DEBUG] Using 'remove last' strategy with length {maxlen_last} and {len(best_matches)} matches.")
    elif maxlen_first > 0:
        best_matches = [m for m in matches_remove_first if m['length'] == maxlen_first]
        best_length = maxlen_first
        print(f"[DEBUG] Using 'remove first' strategy with length {maxlen_first} and {len(best_matches)} matches.")
    # If both are zero, fallback to single words
    if not best_matches:
        for word in words:
            print(f"[DEBUG] Fallback: searching for single word in PDF: '{word}'")
            for page_num in range(doc.page_count):
                page = doc[page_num]
                rects = page.search_for(word)  # type: ignore[reportAttributeAccessIssue]
                for rect in rects:
                    best_matches.append({'page': page_num, 'rect': rect, 'text': word, 'length': 1})
        best_length = 1 if best_matches else 0
    # Filter to only the matches with the longest substring found
    matches = [m for m in best_matches if m['length'] == best_length]
    if not matches:
        print(f"[WARN] No substring matches found in PDF for localization value.")
        return
    # Remove duplicate/overlapping highlights per page (same rect or very close)
    unique_matches = []
    seen = set()
    def rect_key(rect):
        # Round coordinates to avoid floating point issues
        return (rect.x0//2, rect.y0//2, rect.x1//2, rect.y1//2)
    for m in matches:
        key = (m['page'], rect_key(m['rect']))
        if key not in seen:
            unique_matches.append(m)
            seen.add(key)
    matches = unique_matches
    print(f"[DEBUG] Best substring length: {best_length}, unique matches: {len(matches)}")

    # Collect all pages to copy (all pages with matches)
    pages_to_copy = sorted(set(m['page'] for m in matches))

    # Map original page number to new page number in output PDF
    page_map = {orig: idx+1 for idx, orig in enumerate(pages_to_copy)}  # +1 because summary is page 0

    # Always use the output_path argument if provided, otherwise use default
    if output_path:
        output_pdf_path = output_path
    else:
        output_pdf_path = str(Path(pdf_path).with_name(f"{Path(pdf_path).stem}_section_highlighted.pdf"))
    print(f"[DEBUG] Output PDF path: {output_pdf_path}")
    new_doc = fitz.open()  
    for pno in pages_to_copy:
        new_doc.insert_pdf(doc, from_page=pno, to_page=pno)  
        print(f"[DEBUG] Copied page {pno} to new PDF")

    # Highlight all best matches in the new PDF
    for match in matches:
        if match['page'] in pages_to_copy:
            page_idx = pages_to_copy.index(match['page'])
            page = new_doc[page_idx]
            highlight = page.add_highlight_annot(match['rect'])
            highlight.update()
            print(f"[DEBUG] Highlighted match on page {page_idx}")

    # Summary page and hyperlinks removed as requested

    print(f"[DEBUG] Saving output PDF to {output_pdf_path}")
    new_doc.save(output_pdf_path)
    print(f"[INFO] Section-highlighted PDF written to {output_pdf_path}")


def main(pdf_dir: str, md_dir: str, marker: str, output_pdf: str, json_path: Optional[str] = None):
    # If pdf_dir is a directory, use a JSON map to resolve the file
    print(f"[DEBUG] main() called with pdf_dir={pdf_dir}, md_dir={md_dir}, marker={marker}, output_pdf={output_pdf}, json_path={json_path}")
    if os.path.isdir(pdf_dir):
        print(f"[DEBUG] {pdf_dir} is a directory. Resolving JSON map...")
        if not json_path:
            # Look for localizations_map.json in the parent or sibling directory
            json_path = os.path.join(os.path.dirname(pdf_dir), 'localizations', 'localizations_map.json')
            if not os.path.exists(json_path):
                json_path = os.path.join(pdf_dir, 'localizations_map.json')
        print(f"[DEBUG] Using json_path={json_path}")
        if not os.path.exists(json_path):
            print(f"[ERROR] Could not find localizations_map.json near {pdf_dir}")
            return
        import json
        with open(json_path, 'r', encoding='utf-8') as jf:
            print(f"[DEBUG] Loading localization map from {json_path}")
            loc_map = json.load(jf)
        # Try to match marker as @@loc_x@@ or loc_x
        marker_key = marker.strip('@')
        file_name = None
        localization_value = None
        print(f"[DEBUG] marker_key={marker_key}")
        # 1. Direct key match (loc_x)
        if marker_key in loc_map and 'file' in loc_map[marker_key]:
            file_name = loc_map[marker_key]['file']
            localization_value = loc_map[marker_key].get('localization')
            print(f"[DEBUG] Found direct key match: file_name={file_name}, localization_value={localization_value}")
        # 2. @@loc_x@@ match
        if not file_name:
            for k, v in loc_map.items():
                if ('@@' + k + '@@') == marker and 'file' in v:
                    file_name = v['file']
                    localization_value = v.get('localization')
                    print(f"[DEBUG] Found @@loc_x@@ match: file_name={file_name}, localization_value={localization_value}")
                    break
        # 3. Fallback: search in localization value
        if not file_name:
            for v in loc_map.values():
                if 'localization' in v and marker in v['localization'] and 'file' in v:
                    file_name = v['file']
                    localization_value = v.get('localization')
                    print(f"[DEBUG] Found fallback localization match: file_name={file_name}, localization_value={localization_value}")
                    break
        if not file_name:
            print(f"[ERROR] Marker {marker} not found in localization map.")
            return
        # Compose the PDF file path
        pdf_stem = Path(file_name).stem
        pdf_file_path = os.path.join(pdf_dir, pdf_stem +  '.pdf')
        print(f"[DEBUG] Composed PDF file path: {pdf_file_path}")
        if not os.path.exists(pdf_file_path):
            print(f"[ERROR] PDF file does not exist: {pdf_file_path}")
            return
        # Try both .md and .txt.md for the markdown file
        md_path1 = os.path.join(md_dir, pdf_stem, pdf_stem + '.md')
        if os.path.exists(md_path1):
            chosen_md_path = md_path1
        else:
            print(f"[ERROR] Markdown file does not exist: {md_path1}")
            return
        print(f"[DEBUG] Using Markdown file: {chosen_md_path}")
        json_path_md = os.path.join(md_dir, pdf_stem, pdf_stem + '_meta.json')
        print(f"[DEBUG] json_path_md: {json_path_md}")
        extract_sections_with_marker(pdf_file_path, marker, localization_value, output_pdf)
    else:
        print(f"[DEBUG] {pdf_dir} is not a directory. Using as PDF path.")
        # If not a directory, user must provide all paths
        print(f"[ERROR] When not using a directory, you must provide PDF, MD, and JSON paths explicitly.")

if __name__ == "__main__":
    import sys
    default_marker = "@@loc_235@@"
    default_pdf_dir = "../main_storage/exemple2/pdfs"
    default_md_dir = "../main_storage/exemple2/markdown"
    default_output_pdf = "../main_storage/exemple2/debugsections/example.pdf"
    default_json_path = "../main_storage/exemple2/localizations/localizations_map.json"
    if len(sys.argv) < 5:
        print("[DEBUG] Using default arguments:")
        print(f"  pdf_dir: {default_pdf_dir}")
        print(f"  marker: {default_marker}")
        print(f"  output_pdf: {default_output_pdf}")
        print(f"  json_path: {default_json_path}")
        main(default_pdf_dir, default_md_dir,default_marker, default_output_pdf, default_json_path)
    else:
        print(f"[DEBUG] Using sys.argv: {sys.argv}")
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
