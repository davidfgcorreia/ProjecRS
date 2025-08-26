# Project Report — ProjecRS

This document summarizes the current gaps, required fixes, deployment components, estimated cost per iteration, and processing-power guidance for each step of the code pipeline.

Assumptions
- Local dev uses SQLite and small test PDFs (~1–5 MB).
- Production uses PostgreSQL and real PDFs (10–100 MB), and may run LLM calls (OpenAI/Gemini). 
- Cloud pricing and instance sizing are approximate and intended for planning — validate with your provider pricing calculator.

Observed local Docker footprint (measured):
- `projecrs-backend` image: ~13.3 GB
- `projecrs-frontend` image: ~529 MB
- `postgres` image: ~608 MB

Observed memory usage during PDF->MD processing step (from your environment):
- Peak: ~12 GB RAM
- Stable running: ~5 GB RAM

---

## 1) Missing parts & errors to fix (high priority)
Checklist (start here):
- [ ] Remove or replace any accidental assignment to SQLAlchemy Column descriptors. Use instance attributes or table.__dict__.get(...) when manipulating JSON fields.
- [ ] Ensure all Vue SFC templates follow valid HTML rules (no self-closing `<textarea/>`, valid `v-slot` dynamic syntax, `v-for` keys on real elements).
- [ ] Wire API calls for UI actions (example: `findValue` and PDF-overlay save must call `/tabledata/update-cell/` reliably). Confirm error paths surface user-facing errors.
- [ ] Convert debug `print()` statements in processing modules to proper logging and ensure logging is configurable (INFO/WARN/DEBUG). Optionally buffer debug messages and release at end of processing run.
- [ ] Add robust error handling around optional third-party libraries (PyMuPDF, tiktoken, rapidfuzz). Fail gracefully with informative messages and install-time notes.
- [ ] Fix lint / type definition missing files (dev tooling complaining about `.vue-global-types`); add dev dependencies or ignore patterns for CI.
- [ ] Add tests for critical paths: table cell update, upload pipeline, merge operations and an end-to-end processing smoke test.
---

## 2) Components needed for deployment (minimal production configuration)
- Backend API service (FastAPI) behind a reverse proxy (NGINX) or API gateway.
- Frontend static site (Vite) built and served (S3+CloudFront, nginx, or Vercel). Use environment variables for API base URL.
- Database: PostgreSQL (managed service recommended: RDS/Cloud SQL). Use migrations (Alembic) for schema changes.
- Object storage: S3-compatible storage for uploaded PDFs, temporary workspaces and generated reports.
- Worker/Task queue: Celery/RQ or background task framework for processing pipeline & long LLM jobs. Use Redis as broker.
- Secrets manager: pass LLM keys and DB credentials via secrets (Docker secrets, AWS Secrets Manager, Kubernetes secrets).
- Logging & monitoring: central logging (CloudWatch/Stackdriver/ELK) and metrics (Prometheus/Grafana).
- Optional: autoscaling group or Kubernetes cluster for workers if throughput grows.

Deployment notes
- Use Docker and docker-compose for local/dev. Use a CI pipeline to build/publish images and run tests.
- Keep LLM keys server-side. Frontend receives only derived outputs.

---

## 3) Estimated cost per iteration (typical run = process 1 query with N PDFs)
Definitions: "iteration" = one complete processing run for a single `query_id` (upload PDFs → pipeline → store table). Costs are ballpark and intended to help planning.

Small-scale dev (local):

Prodiction (cloud, low load):


Per-PDF cost model (detailed estimates)

The following per-PDF estimates express expected incremental cost for processing and table operations according to the pricing and performance guidance you provided. These are intentionally simple building blocks so you can scale to N PDFs per iteration.

- Local processing (with lightweight LLM assistance): ~ $0.01 per 10 pages.
	- Typical run-time: ~5 minutes on limited resources (small worker). This represents CPU & memory cost only (no external API charges).
- Marker API (accelerated extraction): ~ $0.04 per 10 pages, with an optional performance mode that can reach ~17 pages/second throughput. Add a fixed service overhead of ~$25/month if you keep a paid account or reserved throughput.
- Table operation (post-conversion) using GPT-4.1: ~ $0.02–$0.04 per 10 pages (for file lockups, consolidation and light inference tasks).
- Extra operations (value-finding, descriptions): up to $0.01 per 10 pages for small, repeated operations (for example: many quick "find value" checks across a table).

Example: a single 30-page PDF processed with the mixed pipeline below (1 PDF):

- Local conversion (30 pages): 30/10 * $0.01 = $0.03
- Marker API accelerated pass (optional): 30/10 * $0.04 = $0.12 (+ portion of $25/mo if applicable)
- Table assembly & GPT-4.1 descriptions: 30/10 * $0.03 (mid-range) = $0.09
- Extra find-value ops (10 checks): ~ $0.01
Total (approx) = $0.25 for a 30-page PDF using both local + marker passes and GPT-4.1 table ops. If you skip the Marker API, the same run would be closer to $0.13.

Use these building blocks to compute per-iteration costs: multiply per-PDF totals by N PDFs in a query and add any monthly fixed fees (Marker API reserved capacity, DB, storage, etc.).

1) Upload / Input staging
- Task: Receive files, store to object storage.
- Resources: minimal (API node). 0.5 vCPU, 512 MB–1 GB RAM per API instance.
- Duration: immediate.

2) PDF -> Markdown / extraction (OCR or text extraction)
- Task: run PyMuPDF / marker-based extraction and markdown generation.
- Resources: CPU-bound; recommend 2 vCPU, 4 GB RAM per worker for single concurrent job. For heavy PDFs use 4 vCPU, 8–16 GB RAM.
- Time: small PDF 60-180s; large 200s–500s depending on pages and OCR needs.

3) Parse / table detection / cleanup
- Task: run table parsing, heuristics, merging cells.
- Resources: 1–2 vCPU, 2–4 GB RAM per worker. Parallelize per PDF or per table.
- Time: 2-4s per table.

4) LLM calls (table description, value suggestions)
- Task: network-bound external API calls; CPU minimal but latency matters.
- Resources: small worker (1 vCPU, 2 GB) that issues API calls asynchronously.
- Time & cost: depends on model; round-trip latency 100ms–5s; cost per call varies widely.
- Recommendation: batch requests, cache responses, and add rate limiting.
- Time: 5-25 per table.

5) Table assembly, DB persistence, exports (CSV/XLSX/DOCX/PDF)
- Task: serialization and file generation (openpyxl, python-docx, reportlab).
- Resources: 1–2 vCPU, 2–4 GB RAM per export job. DOCX/PDF generation memory can spike for large tables.
- Time: typically 1–10s per export, can be longer for very large tables.

Parallelism guidance
- For predictable latency, constrain each worker to 1 processing job at a time and scale horizontally.
- For cost efficiency, allow light concurrency for LLM-dominated steps since they spend time waiting for network I/O.

---

## 5) Recommendations & next steps (practical roadmap)
1. Stability
- Fix the critical router/path issues and template errors so the frontend compiles without warnings.
- Harden backend endpoints (validation, error messages) and fix SQLAlchemy descriptor misuse.

2. Observability
- Replace remaining `print()` debug traces in processing modules with `logging.debug()` and configure one central logger. Optionally buffer debug logs per-run and return them in API response only when requested (for diagnostics).

3. Efficiency
- Batch LLM requests where possible. Cache model outputs per (query_id, prompt fingerprint).
- Use worker autoscaling and spot instances for batch-heavy processing.

4. Testing & CI
- Add unit tests for table updates, merges, and the modular processing caller. Add a lightweight e2e test (upload small PDF, run pipeline, fetch table).

5. Cost control
- Add a cost-monitoring dashboard: track LLM spend, worker-hours, and storage usage. Add alerts on threshold.

---

If you want, I can:
- Generate a prioritized, timeboxed ticket list from this report.
- Create a CI workflow for running the critical tests and building images.
- Create a small diagnostics endpoint to return buffered debug logs for a `query_id` after processing completes.

Tell me which follow-up you want and I'll implement it.
