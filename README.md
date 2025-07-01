# FastAPI Minimal Backend

A minimal, modular FastAPI backend with SQLAlchemy ORM and PostgreSQL (or SQLite fallback). Includes a simple User model and CRUD endpoints.

## Features
- FastAPI backend
- SQLAlchemy ORM
- PostgreSQL (or SQLite for local/dev)
- Docker & docker-compose for production
- Modular structure, ready to scale

## Usage

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up the database (SQLite by default):
   ```bash
   python -c 'from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)'
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### With Docker Compose
1. Build and start services:
   ```bash
   docker-compose up --build
   ```
2. The API will be available at http://localhost:8000

## API Endpoints
- `POST /users/` — Create user
- `GET /users/` — List users
- `GET /users/{id}` — Get user by ID
- `PUT /users/{id}` — Update user
- `DELETE /users/{id}` — Delete user
