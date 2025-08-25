# Backend API Documentation

This folder contains the FastAPI route modules for the ProjecRS backend. Each file defines a set of endpoints for a specific feature or resource in the application.

## API Modules Overview

- `user.py`: User authentication, registration, and management endpoints.
- `upload.py`: Endpoints for uploading files and handling file storage.
- `result.py`: Endpoints for retrieving and managing query results.
- `table_data.py`: Endpoints for accessing, updating, and describing tabular data.
- `localization.py`: Endpoints for localization and language support.
- `highlight_header.py`: Endpoints for highlighting header values in PDFs and other documents.
- `download.py`: Endpoints for downloading exported files in various formats (CSV, XLSX, PDF, DOCX).

## Usage
- Each file defines a FastAPI router and related request/response models.
- Routers are included in the main application (`main.py`).
- Endpoints are documented with docstrings and type hints for clarity.

---
For details on each API, see the inline documentation in the respective files.
