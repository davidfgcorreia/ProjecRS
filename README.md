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
1. Build and start backend, db, and frontend:
   ```bash
   docker-compose up --build
   ```
   - The API will be available at http://localhost:8000
   - The frontend will be available at http://localhost:5173

2. To run backend tests in Docker:
   ```bash
   docker-compose run --rm test
   ```

3. To start only the backend and db (no frontend):
   ```bash
   docker-compose --profile db --profile backend up --build
   ```

4. To stop all services:
   ```bash
   docker-compose down
   ```

## API Endpoints
- `POST /users/` — Create user
- `GET /users/` — List users
- `GET /users/{id}` — Get user by ID
- `PUT /users/{id}` — Update user
- `DELETE /users/{id}` — Delete user
- `GET /tabledata/` — Get table data by query_id
- `POST /tabledata/filled/` — Process and store table data

## Notes
- Make sure Docker is running before using Docker Compose commands.
- For production, configure environment variables in `.env`.
