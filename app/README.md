# App (FastAPI backend)

This folder contains the project's FastAPI backend: API endpoints, database models/CRUD,
processing pipeline entrypoints, and services (exports, LLM integration, file storage).

Key files and folders

- `main.py` — FastAPI application entrypoint.
- `init_db.py` — helper to initialize or reset the database (create tables, seed data).
- `api/` — HTTP route modules (upload, download, table_data, result, user, etc.).
- `db/` — database configuration and CRUD helpers (`database.py`, `crud.py`).
- `models/` — SQLAlchemy model definitions for persistent entities.
- `schemas/` — Pydantic request/response schemas.
- `services/` — application services (file storage, table export, LLM table description).
- `processing_operation/` — document processing pipeline and small operation modules.
- `storage/` — sample storage areas used by the pipeline (pdfs, markdowns, temporary, reports).

Overview

The backend is implemented with FastAPI and SQLAlchemy. It defaults to an SQLite database for local
development, but can be configured to use PostgreSQL or other DBs via `DATABASE_URL` environment
variable. The application exposes CRUD and file-processing endpoints and contains helpers
for exporting tables (CSV/XLSX/DOCX/PDF) and generating on-demand table descriptions
using an LLM service.

Quickstart (local)

1. Create and activate the virtualenv (project venv is under `.venv` if you use the repo's
   provided environment):

   ```bash
   # from repo root
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables (example `.env`):

   ```env
   DATABASE_URL=sqlite:///./test.db
   OPENAI_API_KEY=sk-...
   ````

3. Initialize DB (runs `init_db.py` which uses SQLAlchemy metadata):

   ```bash
   .venv/bin/python app/init_db.py
   ```

4. Run the API server (development):

   ```bash
   .venv/bin/python -m uvicorn app.main:app --reload --port 8000
   ```

API docs are available at `http://localhost:8000/docs` (Swagger UI).

Processing pipeline

- The pipeline entrypoints are `app/processing_operation/clinical_pdf_pipeline.py` and
  `app/processing_operation/modular_processing_caller.py`.
- The folder `app/processing_operation/operarions` contains many small step scripts (pdf→md,
  table extraction, LLM prompts, merging, formatting). A README is provided inside that folder
  (`operarions/README.md`) with per-step guidance.
- Some operations require optional packages: `PyMuPDF`, `rapidfuzz`, `pandas`, `tiktoken`, etc.
  Install them only when needed.

Exports and LLM

- Table export logic lives in `app/services/table_export.py` and supports CSV, XLSX, DOCX, and
  PDF (guarded optional imports). If an optional dependency is missing the service raises a
  clear error.
- Table descriptions are generated on-demand by `app/services/table_description_llm.py` and are
  not persisted to the database (by design).

Docker

- A `Dockerfile` and `docker-compose.yml` exist at the repository root for containerized runs.
  Adjust environment variables in `docker-compose.yml` before `docker compose up`.

Testing

- Unit tests are under `tests/` — run them with `pytest` inside the venv:

  ```bash
  .venv/bin/python -m pytest -q
  ```

Troubleshooting

- Permission errors writing to `processing_operation/main_storage` often mean the process
  user doesn't own the folder. Fix with:

  ```bash
  sudo chown -R "$USER:$USER" app/processing_operation/main_storage
  chmod -R u+rwX app/processing_operation/main_storage
  ```

- Optional-external-library imports are guarded in code; install the package listed in the
  module docstring or the top-level `requirements.txt` if missing.

Contributing

- Keep operation modules small and testable. Add unit tests for parsing/merge/format routines
  under `tests/processing` when updating behavior.
- Document any new optional dependency in this README and `requirements.txt`.