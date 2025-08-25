# Full Project Documentation

## Overview

This repository contains a full-stack application with a Python FastAPI backend and a Vue 3 frontend. The project is organized to support local development with SQLite and production with PostgreSQL, and it includes Docker configuration for containerized development and deployment.

Core components:
- Backend: FastAPI + SQLAlchemy (PostgreSQL for production, SQLite as a local fallback)
- Frontend: Vue 3 (Vite)
- Containerization: Docker + docker-compose
- Tests: Pytest for backend (tests/), optional Vitest/Cypress for frontend
- Main features: user CRUD, PDF upload and processing, authentication, result export (CSV/XLSX/DOCX/PDF), simple role-based permissions (user/admin)

Note: the frontend <-> backend integration is under active development; some endpoints or payload shapes may change. Use the API docs exposed by the backend (Swagger UI) as the source of truth during development.

---

## Repository structure

```
ProjecRS/
├── app/                    # FastAPI application (backend)
│   ├── api/                # Route modules (user, upload, result, etc.)
│   ├── db/                 # Database config and CRUD helpers
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business services (file storage, exports, LLM helpers)
│   └── main.py             # FastAPI app factory / run entry
├── frontend/               # Vue 3 application (Vite)
│   ├── src/                # Vue app source (components, views, api, stores)
│   └── README.md           # Frontend-specific docs
├── tests/                  # Backend unit and integration tests (pytest)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Backend Dockerfile
├── docker-compose.yml     # Compose orchestration (db, backend, frontend)
└── DOCUMENTACAO.md         # This document (project-level docs)
```

---

## How to run (development)

### Backend (local, using Python virtual environment)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and initialize DB:

```bash
pip install -r requirements.txt
python -m app.init_db   # creates local SQLite db and default admin user if configured
```

3. Run the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

The interactive API docs will be available at http://localhost:8000/docs

### Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (usually http://localhost:5173). Configure `VITE_API_BASE_URL` in `frontend/.env` if backend runs on a different host/port.

### Run everything with Docker Compose

```bash
docker-compose up --build
```

Services launched by compose (typical):
- Backend API: http://localhost:8000
- Frontend (Vite preview or proxy): http://localhost:5173

To run only backend and DB (skip frontend):

```bash
docker-compose --profile db --profile backend up --build
```

To stop and remove containers:

```bash
docker-compose down
```

---

## Environment variables

Common environment variables used by the project:

- `DATABASE_URL` — SQLAlchemy URL for the database (e.g. `postgresql://user:pass@db:5432/appdb` or `sqlite:///./dev.db`).
- `SECRET_KEY` — application secret used for session tokens or other cryptographic operations.
- `VITE_API_BASE_URL` — frontend-only variable used by the client to call the backend (must be prefixed with `VITE_`).
- `LOG_LEVEL` — backend logging level (optional).

LLM / AI integration variables
--------------------------------
- `OPENAI_API_KEY` — (backend) API key used by server-side LLM calls (for OpenAI or compatible providers). Set this in the backend environment; do NOT expose it to the browser.
- `GEMINI_API_KEY` — (backend) API key used to call Google's Gemini (or other named LLM provider). Keep this secret and do NOT expose it to client-side code.
- `LLM_PROVIDER` — optional (backend) string to identify provider (e.g., `openai`, `gemini`, `azure`, `local`).
- `VITE_LLM_ENABLED` — frontend flag (true/false) used to enable or disable client-side UI for LLM features (must be prefixed with `VITE_`).

Important security note:
- LLM API keys are sensitive credentials. They must be kept on the server side and never embedded directly in client-side code. When the frontend needs LLM functionality, it should request the backend which will call the LLM provider and return non-sensitive results.
- For local development, store LLM keys in the backend `.env` (or the environment of your development shell) and avoid committing this file to the repository. Example backend `.env`:

```bash
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=changeme
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

If you use Docker, pass secrets into the container using environment variables or a secrets manager (Docker Secrets, AWS Secrets Manager, etc.).

For clarity, here is an example JSDoc-style comment describing the Gemini key (DO NOT place the real key in source files):

```javascript
/**
 * GEMINI_API_KEY is a constant that stores the API key required to authenticate requests to the Gemini API.
 * This key should be kept secure and not exposed in client-side code or public repositories.
 *
 * @constant
 * @type {string}
 */
// const GEMINI_API_KEY = process.env.GEMINI_API_KEY
```

Place runtime variables in a `.env` file for local development or configure them via your deployment environment. Example `.env` for frontend (Vite):

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENABLE_MOCK=false
```

---

## Main backend endpoints (summary)

These are the common endpoints implemented in the backend; use `/docs` for exact payloads and schemas.

- `POST /users/` — create a new user (fields: name, email, password)
- `GET /users/` — list users
- `GET /users/{id}` — get user details
- `PUT /users/{id}` — update user
- `DELETE /users/{id}` — delete user
- `POST /upload/pdf/` — upload a PDF for processing (requires authentication)
- `GET /tabledata/{query_id}` — fetch processed table data for a query
- `POST /tabledata/filled/` — store/submit edited table data
- `POST /table/merge-columns` — merge two columns in a stored table (example)

The backend also exposes an endpoint for requesting on-demand LLM table descriptions and highlighted PDF snippets used by the UI.

---

## Authentication & security

- The project uses a minimal authentication system. Passwords are stored hashed (original implementation used SHA-256).
- A `role` field distinguishes regular users from admins; role checks are enforced in some admin routes.
- A default admin account may be created by `app.init_db` for convenience in development (check the script for credentials and change them).

Security notes:
- In production, prefer a strong password hashing function (bcrypt/argon2) rather than plain SHA-256.
- Protect sensitive environment variables and never commit them to version control.

---

## Tests

- Backend unit and integration tests use pytest and are located under `tests/`.
  Run them like:

```bash
pytest -q
```

- Frontend tests (if configured) may use Vitest or Cypress. Check `frontend/package.json` for available scripts.

---

## Integration notes & troubleshooting

- The frontend and backend must agree on request/response schemas. Use the OpenAPI docs exposed by FastAPI (`/docs`) to confirm shapes.
- Common errors:
  - 422 validation errors: usually caused by mismatched field names or payload shapes.
  - CORS errors: configure `CORSMiddleware` in the backend to allow requests from the frontend origin during development.

If the processing pipeline or file storage fails with permission errors, verify that the `app/processing_operation/main_storage` and subfolders are writable by the application user.

---

## Docker notes

- Backend and frontend are built in separate containers. The `docker-compose.yml` defines service names and networks.
- Database volumes are used to persist PostgreSQL data between restarts. To reset local SQLite, remove the DB file (for dev only).

---

## Maintenance & scalability

- Code is organized in a modular way (routes, services, models) to make it easier to add features.
- For production deployments, use a managed database, enable HTTPS, run background workers for long-running processing tasks, and add proper monitoring.
- Add Alembic for DB migrations if you plan schema changes—this repo is structured to allow Alembic to be added later.

---

If you want, I can:
- Add example request payloads for each endpoint in this document.
- Add a short deployment guide for a cloud provider (DigitalOcean, AWS ECS, or Kubernetes).
- Harden the authentication to use bcrypt/argon2 and refresh tokens.

Send me which of the above you'd like next and I'll apply it.
