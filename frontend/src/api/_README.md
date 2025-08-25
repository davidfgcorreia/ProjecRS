# Frontend API services

This folder contains small wrapper modules that call the backend HTTP API. Each file exports functions used by the UI to perform network operations (upload, download, table CRUD, LLM requests, etc.).

Purpose

- Keep network code separated from UI components.
- Provide typed/centralized places to adjust endpoint URLs, headers, and error handling.
- Make mocking easier for tests.

Modules

- `downloadService.js` — Helpers to download generated files (exports, reports).
- `highlightHeaderService.js` — Requests to the backend to perform header highlighting operations.
- `localizationService.js` — Endpoints related to localization data and maps.
- `mergeCellService.js` — API calls for merging table cells on the server.
- `resultService.js` — Endpoints related to processing results and reports.
- `tableDataService.js` — CRUD and updates for table rows/cells.
- `tableDownloadService.js` — Wrapper for table-specific download endpoints (CSV/XLSX/DOCX/PDF).
- `upload.js` — File upload endpoints (PDFs and auxiliary files).
- `userService.js` — User management (login, profile).

Usage

Import the service in a component or store and call the exposed function(s):

```js
import { downloadFile } from '@/api/downloadService'

await downloadFile(queryId, 'xlsx')
```

Testing

- Services are small and easy to mock. In Jest/Vitest tests, mock the HTTP client used by the services (axios/fetch wrapper) and assert calls and parameters.

Notes

- Keep endpoint paths in one place to simplify updates.
- Centralize auth header handling in the HTTP client (e.g., axios instance) rather than in every service file.
