# Standard library imports
import os
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
import openai

# --- CONFIGURATION ---
DEFAULT_HEADER = "Region"
DEFAULT_PDF_PATH = "../main_storage/exemple2/pdfs/Eichenfield 2021.pdf"
DEFAULT_OUTPUT_DIR = "../main_storage/exemple2/completed_highlights"
DEFAULT_MODEL = "gpt-4.1-mini-2025-04-14"

# --- SYSTEM PROMPT FOR CHATGPT ---
SYSTEM_PROMPT = (
    "You are an expert in clinical trial data extraction. "
    "Given a header name, provide a Python list of 50 example values that are typically found immediately next to this header value in real clinical trial PDFs. "
    "Note: Some values that might be expected to be a number or a simple term can actually appear as extended descriptive phrases in the PDF. For example, for the header 'RCT phase', the value may be written as 'double-blind, placebo-controlled' or similar text, not just 'Phase 3'. However, do not use full long phrases—prefer short sections or fragments of these phrases (e.g., 'double-blind', 'placebo-controlled', 'randomized', 'multicenter') for better matching and highlighting. "
    "For example, if the header is 'ClinicalTrials.gov number' or 'RCT identifier', the values should be registry prefixes (like 'NCT', 'ISRCTN'), URLs (like 'https://clinicaltrials.gov'), or correlated keywords (like 'number', 'identifier', 'registration'). Do not guess or generate example numbers. "
    "Do not try to guess or infer the value. Only provide correlated keywords, registry prefixes, URLs, or descriptive phrases that are directly related to the header and can be found by a direct text search in the PDF. Do not generate or guess numbers. "
    "Focus on values that are actually found immediately after or before the value indicated for the header in real clinical trial PDFs, and that can be found by a simple text search. "
    "Return only a valid Python list of strings, no explanations, no extra text."
)

def get_possible_values(header: str, model: str = DEFAULT_MODEL) -> List[str]:
    """
    Query OpenAI's GPT model to get a list of 50 possible values for a given header, using the same request style as run_llm_debug_sections.py.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Header: {header}"}
        ],
        max_tokens=512,
        temperature=0.7,
    )
    import ast
    content = response.choices[0].message.content
    if not content or not isinstance(content, str):
        return []
    try:
        values = ast.literal_eval(content)
        if isinstance(values, list):
            return [str(v) for v in values]
        else:
            print("[WARN] LLM did not return a list, falling back to line split.")
            return [line.strip('-* ') for line in content.splitlines() if line.strip()]
    except Exception as e:
        print(f"[WARN] Could not parse LLM output as list: {e}. Falling back to line split.")
        return [line.strip('-* ') for line in content.splitlines() if line.strip()]

def highlight_words_in_pdf(pdf_path: str, words: List[str], output_path: Optional[str] = None):
    """
    Copy the original PDF and highlight all occurrences of the given words.
    # type: ignore[reportAttributeAccessIssue]  # Pyright/mypy: ignore dynamic PyMuPDF attributes
    """
    doc = fitz.open(pdf_path)  # type: ignore[reportAttributeAccessIssue]
    new_doc = fitz.open()  # type: ignore[reportAttributeAccessIssue]
    for page_num in range(doc.page_count):
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)  # type: ignore[reportAttributeAccessIssue]
    # Count total occurrences of each word in the document
    word_counts = {}
    for word in words:
        total = 0
        for page_num in range(new_doc.page_count):
            page = new_doc[page_num]
            total += len(page.search_for(word))  # type: ignore[reportAttributeAccessIssue]
        word_counts[word] = total

    for page_num in range(new_doc.page_count):
        page = new_doc[page_num]
        for word in words:
            if word_counts.get(word, 0) > 20:
                continue  # Skip highlighting this word
            rects = page.search_for(word)  # type: ignore[reportAttributeAccessIssue]
            for rect in rects:
                highlight = page.add_highlight_annot(rect)  # type: ignore[reportAttributeAccessIssue]
                highlight.update()  # type: ignore[reportAttributeAccessIssue]
    if not output_path:
        output_path = str(Path(pdf_path).with_name(f"{Path(pdf_path).stem}_highlighted.pdf"))
    new_doc.save(output_path)  # type: ignore[reportAttributeAccessIssue]
    print(f"[INFO] Highlighted PDF saved to {output_path}")

def main(header: str, pdf_path: str = DEFAULT_PDF_PATH, output_dir: str = DEFAULT_OUTPUT_DIR, model: str = DEFAULT_MODEL):
    """
    Given a header name and a PDF file path, outputs a PDF with possible values for this header highlighted.
    """
    print(f"[DEBUG] Requesting possible values for header: {header}")
    values = get_possible_values(header, model)
    print(f"[DEBUG] Got {len(values)} possible values from model.")
    for idx, val in enumerate(values, 1):
        print(f"[DEBUG] Value {idx}: {val}")
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.exists() or not pdf_path_obj.is_file():
        print(f"[ERROR] PDF file not found: {pdf_path_obj}")
        return
    os.makedirs(output_dir, exist_ok=True)
    output_path = str(Path(output_dir) / f"{pdf_path_obj.stem}_highlighted.pdf")
    print(f"[DEBUG] Processing {pdf_path_obj} -> {output_path}")
    highlight_words_in_pdf(str(pdf_path_obj), values, output_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"[INFO] No header provided, using default header: '{DEFAULT_HEADER}'")
        header = DEFAULT_HEADER
        pdf_path = DEFAULT_PDF_PATH
        output_dir = DEFAULT_OUTPUT_DIR
        model = DEFAULT_MODEL
    else:
        header = sys.argv[1]
        pdf_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PDF_PATH
        output_dir = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_OUTPUT_DIR
        model = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_MODEL
    main(header, pdf_path, output_dir, model)
