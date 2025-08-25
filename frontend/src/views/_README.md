# Views

This folder contains the main page views used by the frontend SPA. Each view is a single-file Vue component (SFC) and is designed to be light on logic — heavy lifting belongs in services or composables under `frontend/src/api` and `frontend/src/stores`.

Overview of views

- `UploadView.vue`
  - Purpose: Accepts user file uploads.
  - Key actions: Validate file types/sizes, POST files to backend, show progress.

- `ChooseTableView.vue`
  - Purpose: Allow users to choose which indexes to use in the final table.

- `ResultView.vue`
  - Purpose: Primary validation/editor view showing the extracted table.
  - Key actions: Edit cell values, open context menus for localization, merge cells/columns, and navigate to preview/export.

- `PreviewView.vue`
  - Purpose: Final read-only preview and export actions (CSV/XLSX/DOCX/PDF).
  - Key actions: Choose export format and download the processed table.

- `LoginView.vue`
  - Purpose: Authenticate users.
  - Key actions: Sign in with credentials, store user info in Pinia.

- `RegisterView.vue`
  - Purpose: Register new users.
  - Key actions: Collect user details, call registration API, and optionally sign in.

Notes for contributors

- Keep view logic minimal. Put API calls into `frontend/src/api/*` files and state into `frontend/src/stores/*`.
- Use the `BaseLayout.vue` component for consistent site chrome. Place any per-view header controls into the `header-right` slot if needed.
- When adding new views, remember to add route entries in `frontend/src/router` and document the route's purpose here.
