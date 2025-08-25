# Frontend (Vue 3 + Vite)

This folder contains the single-page application for ProjecRS, built with Vue 3 and Vite.
The app uses `<script setup>` SFCs, Pinia for state, Vue Router for navigation and a small set
of API services under `src/api` to talk to the FastAPI backend.

Summary
-------
- Framework: Vue 3 + Vite
- State: Pinia (stores under `src/stores`)
- Routing: Vue Router (`src/router`)
- Views: `src/views` (Upload, ChooseTable, Result, Preview, Login, Register)
- Services: `src/api/*` (HTTP client wrappers used by views)
- Layout: `src/components/BaseLayout.vue` is the application shell used by `App.vue`.

Project structure (important folders)
------------------------------------
- `src/main.js` - app bootstrap (Pinia, router, global CSS)
- `src/App.vue` - root component (renders `BaseLayout` + `<router-view/>`)
- `src/components/` - reusable UI components and layout
- `src/views/` - page views (each view is an SFC) — see `src/views/README.md` for details
- `src/api/` - small modules wrapping backend calls (tableDataService, upload, userService, etc.)
- `src/stores/` - Pinia stores (global state such as `userId` and `queryId`)

Frontend logic overview
-----------------------
- Upload flow: `UploadView.vue` accepts files and sends them to the backend upload endpoint. On success
	the backend returns a `query_id` used to fetch processed table data.
- Table selection & validation: `ChooseTableView.vue` and `ResultView.vue` let users pick tables,
	edit values, merge columns/cells and request highlighted PDF snippets from the backend.
- Preview & export: `PreviewView.vue` shows a read-only preview and calls the backend export endpoints
	to download CSV/XLSX/DOCX/PDF formats.
- Authentication: `LoginView.vue` and `RegisterView.vue` call the user API services and store minimal
	user info in Pinia/localStorage.

API contract (high-level)
------------------------
The frontend uses the small service modules in `src/api` which expect a REST API backend. Typical
actions performed by the frontend services:

- Upload files and start processing -> returns a `query_id`.
- Fetch table data for a `query_id` (table contents, column metadata).
- Update a single table cell (row/col) when a user edits a value.
- Merge columns or merge cells (row-level merge) on demand.
- Request highlighted PDF snippets for a specific marker and row (used by localization features).

Note: exact endpoint paths and payloads live in the service modules (search `src/api` to inspect).

Environment
-----------
Create a `.env` file in `frontend/` or set environment variables in your shell. Vite requires variables
prefixed with `VITE_` to be exposed to the client.

Recommended vars (example `.env`):

VITE_API_BASE_URL=http://localhost:8000/api
VITE_FRONTEND_PORT=5173
VITE_ENABLE_MOCK=false

- `VITE_API_BASE_URL` — base URL of the backend REST API (used by service modules).
- `VITE_FRONTEND_PORT` — port to run Vite dev server (optional, default 5173).
- `VITE_ENABLE_MOCK` — when `true`, some services may return local mock data for development.

Run (development)
-----------------
1. Install dependencies

```bash
cd frontend
npm install
```

2. Start dev server

```bash
npm run dev
```

Open the URL printed by Vite (usually http://localhost:5173). The frontend will call the backend configured
in `VITE_API_BASE_URL`.

Build & preview (production)
----------------------------
```bash
npm run build
npm run preview
```

Docker
------
There is a `frontend/Dockerfile` in the repository. For full-stack development you can use the
top-level `docker-compose.yml` to build both frontend and backend as services. Example:

```bash
docker-compose up --build
```

Testing & linting
-----------------
- If the project includes lint/test scripts in `package.json`, run them locally before creating PRs:

```bash
npm run lint   # if configured
npm run test   # if configured
```

Contributing
------------
- Branching: create feature branches named `feat/xxx` or fix branches `fix/xxx` and open a PR to `main`.
- Commits: write small, focused commits with descriptive messages.
- Code style: follow existing conventions (SFCs use `<script setup>`). Run the linter and tests locally.
- Docs: update `src/views/README.md` and this README when you add or change views or API interactions.
- Reviews: include a brief description of how to manually test your changes in the PR description.

Developer tips
--------------
- Keep view components light: put API calls in `src/api/*.js` and state in Pinia stores.
- Use the `BaseLayout.vue` header `header-right` slot to add small user controls (profile, logout) that should
	appear on all pages.
- Many UI features (table editing, merging) rely on backend support. If you are developing frontend-only
	features, set `VITE_ENABLE_MOCK=true` and implement or extend the mock modules under `src/api`.

Where to look next
------------------
- `src/views/README.md` — short description of each view (already included in the repo).
- `src/api/` — concrete API wrappers and request shapes used by the UI.
- `src/stores/` — global store and persistence logic (Pinia).

If you'd like I can:
- Run the dev server and capture build output here.
- Add a small CONTRIBUTING.md with PR templates and checklist items.
- Wire a small profile area into the header using `header-right` and the Pinia store.

