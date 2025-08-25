# Processing operations

This folder contains small, focused helper scripts used by the processing pipeline in
`app/processing_operation` (the clinical PDF -> markdown -> table -> LLM pipeline).
Each module implements a single transformation or utility and is designed to be
runnable individually for debugging or composable from the higher-level pipeline.

## Purpose

- Keep per-step logic small and testable (e.g. PDF → markdown, table extraction, merging,
  LLM prompting helpers, localization helpers, file copy utilities).
- Allow running a single step locally during development or debugging.
- Provide building blocks used by `clinical_pdf_pipeline.py` and `modular_processing_caller.py`.

## Key modules

- `pdf_to_markdown.py` — convert PDFs into markdown and metadata JSON files.
- `copy_all_tables_to_single_md.py` — collect tables from markdown into single-table files.
- `extract_titles.py` — extract section titles and nearby content from markdown.
- `find_section_by_marker.py` — locate and highlight sections in PDFs using markers.
- `generate_markdown_table_clean.py` — produce cleaned merged markdown tables from parsed values.
- `process_tables.py` — post-process markdown tables (formatting, normalization).
- `merge_md_columns.py` / `merge_columns.py` — helpers to merge columns in markdown tables.
- `merge_cells.py` — merges adjacent cell values during post-processing.
- `merge_output_indexes.py` / `parse_output_indexes.py` / `parse_index_2.py` — parsing/merging LLM outputs.
- `localizations.py` — localization extraction and mapping utilities.
- `run_llm_prompt_*` / `run_llm_debug_*` — debugging tools that drive prompts to the LLM services.

(Full file list is available in the repository; modules are intentionally small.)

## Dependencies

Many operation modules use optional third-party packages. Install the project's venv and then:

```bash
# from repo root
. .venv/bin/activate
pip install -r requirements.txt
# Optional packages used by operations (install as needed):
pip install PyMuPDF rapidfuzz pandas tiktoken python-docx openpyxl reportlab
```

Notes:
- `PyMuPDF` (imported as `fitz`) is used by PDF search/highlight helpers.
- `rapidfuzz` is used for fuzzy matching utilities.
- `tiktoken` is used by LLM-related helper scripts.
- Some modules only need optional deps at runtime; the code guards imports where possible.

## Usage examples

Run a single operation for debugging:

```bash
# run find_section_by_marker with defaults (module has CLI defaults)
python app/processing_operation/operarions/find_section_by_marker.py

# convert a single markdown table to docx/xlsx (standalone tool)
python app/processing_operation/operarions/md_to_docx_xlsx.py path/to/table.md path/to/output_dir
```

Run the full pipeline (entrypoint):

```bash
python app/processing_operation/clinical_pdf_pipeline.py
# or use modular_processing_caller.py for per-query runs
```

## Permissions & storage

The pipeline writes into `app/processing_operation/main_storage` (or folders under `exemple2`).
Make sure the process user owns and can write to these directories. Example:

```bash
sudo chown -R "$USER:$USER" app/processing_operation/main_storage
chmod -R u+rwX app/processing_operation/main_storage
```

## Testing / Debugging

- Run individual scripts against a small sample file to validate behavior.
- Use the `run_llm_debug_*` variants to test prompt flows without changing persisted data.
- Logs and `print()` debug lines are present in many modules to help trace behavior.

## Contributing / Extending

- Keep operation functions focused and side-effect free where possible.
- Add small unit tests under `tests/processing` when you change parsing/merge logic.
- Document any new optional dependency in this README and `requirements.txt`.

## Contact / Notes

If something in the folder behaves unexpectedly, run the corresponding module directly with a small input and post the debug output. The pipeline expects JSON-backed markdown metadata in the same folders — keep those files in sync when testing individual steps.
