"""
Main entry point for the ProjecRS FastAPI backend.

This file sets up the FastAPI application, configures CORS, loads environment variables, and includes all API routers.
It also ensures the database is initialized and the admin user exists on startup.

Routers included:
    - user, upload, result, table_data, localization, highlight_header, download

Usage:
    Run with: uvicorn app.main:app --reload
    Set environment variables as needed (e.g., DATABASE_URL)
"""
from fastapi import FastAPI 
from dotenv import load_dotenv 
from fastapi.middleware.cors import CORSMiddleware 
from app.api import user
from app.api import upload
from app.api import result
from app.api import table_data
from app.api import localization
from app.api import highlight_header
from app.api import download
from app.db.database import Base, engine, init_admin_user
import time
from sqlalchemy.exc import OperationalError 
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    max_tries = 10
    for i in range(max_tries):
        try:
            Base.metadata.create_all(bind=engine)
            init_admin_user()
            break
        except OperationalError as e:
            print(f"Database not ready, retrying in 3s... ({i+1}/{max_tries})")
            time.sleep(3)
    else:
        raise RuntimeError("Database connection failed after retries.")
    yield
    # (Optional) Add shutdown logic here


# Load .env for local development (has no effect in Docker if env vars are set by Docker)
load_dotenv()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(upload.router)
app.include_router(result.router)
app.include_router(table_data.router)
app.include_router(localization.router)
app.include_router(highlight_header.router)
app.include_router(download.router)