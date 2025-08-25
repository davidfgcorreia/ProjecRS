"""
Database initialization script for ProjecRS backend.

This script creates all database tables defined in the models and ensures the default admin user exists.
It should be run during initial setup or after migrations to prepare the database for use.

Usage:
    python app/init_db.py
    # Optionally set DATABASE_URL to use a specific database
"""
import os
from app.db.database import Base, engine, init_admin_user
from app.models import *

def init_db():
    print("[INIT] Creating all tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("[INIT] Ensuring admin user exists...")
    init_admin_user()
    print("[INIT] Database initialization complete.")

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    print(f"[INIT] Using DB: {db_url}")
    init_db()
