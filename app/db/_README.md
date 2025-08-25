# Database Module Documentation

This folder contains the database layer for the ProjecRS FastAPI backend. It provides configuration, session management, and CRUD utilities for interacting with the application's database.

## Database Type
- **Default:** SQLite (for local development and testing)
- **Production:** PostgreSQL (recommended, set via the `DATABASE_URL` environment variable)

## Files Overview

### `database.py`
- **Purpose:** Sets up the SQLAlchemy engine, session factory, and base model class.
- **Key Features:**
  - Reads `DATABASE_URL` from environment (defaults to SQLite).
  - Creates `engine` and `SessionLocal` for main DB, and `TestEngine`/`TestSessionLocal` for testing.
  - Provides `get_db()` dependency for FastAPI routes.
  - Includes password hashing and admin user initialization utilities.

### `crud.py`
- **Purpose:** (To be documented based on actual content)
- **Key Features:**
  - Contains CRUD (Create, Read, Update, Delete) helper functions for database models.
  - Used by API routes and services to interact with the database in a modular way.

### `__init__.py`
- **Purpose:** Marks the folder as a Python package.
- **Key Features:**
  - Typically empty or used for package-level imports.

## Usage
- Import `SessionLocal` and `Base` from `database.py` in your models and services.
- Use the CRUD functions from `crud.py` for database operations.
- Configure your database by setting the `DATABASE_URL` environment variable.

## Example Database URLs
- **SQLite (default):** `sqlite:///./test.db`
- **PostgreSQL:** `postgresql://user:password@localhost/dbname`

## Migrations
- Use Alembic or a similar tool for database migrations if you change your models.

---
For more details, see the inline documentation in each file.
