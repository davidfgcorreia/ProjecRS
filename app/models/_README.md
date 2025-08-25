# Models Documentation

This folder contains the SQLAlchemy ORM models for the ProjecRS backend. Models define the structure of the database tables and are used throughout the application for data storage and retrieval.

## Currently Used Models

### `user.py`
- **Purpose:** Defines the `User` model for authentication, authorization, and user management.
- **Fields:** id, name, email, password (hashed), role, etc.
- **Usage:** Used for login, registration, and admin/user role management.

### `table_data.py`
- **Purpose:** Defines the `TableData` model for storing tabular data extracted from uploaded files and processed queries.
- **Fields:** id, query_id, userid, num_rows, row_ids, columns_content, etc.
- **Usage:** Used for all table-related operations, including export, preview, and LLM-powered description.

## Models To Be Implemented
- `query_file.py`
- `query.py`
- `uploaded_file.py`

These files are placeholders for future features and are not actively used in the current version.

## Usage
- Import models in your API, services, and database scripts to interact with the database.
- Models are mapped to database tables via SQLAlchemy and are used for CRUD operations.

---
For details on each model, see the inline documentation in the respective files.
