from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user
from app.api import upload
from app.api import result
from app.db.database import Base, engine, init_admin_user
import time
from sqlalchemy.exc import OperationalError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para produção, especifique o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(upload.router)
app.include_router(result.router)


@app.on_event("startup")
def on_startup():
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
