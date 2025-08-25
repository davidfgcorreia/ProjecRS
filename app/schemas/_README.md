Schemas directory

This folder contains Pydantic schema modules used by the FastAPI application to define
request and response shapes for the API. Each file defines one or more Pydantic models
that mirror the database models (in `app/models`) or describe API payloads.

Files:
- `query_file.py` - Schemas related to uploaded query files and processing metadata.
- `query.py` - Schemas for query parameters and query-related payloads.
- `table_data.py` - Schemas describing table structure and cell content exchanged via the API.
- `uploaded_file.py` - Schemas for uploaded file metadata and storage details.
- `user.py` - Schemas for user creation, authentication and public user data.

Usage:
Import the Pydantic models from these modules in routers and services to validate
and serialize API input/output consistently.
