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
