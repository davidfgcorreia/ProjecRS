from fastapi import FastAPI
from app.api import user
from app.api import upload
from app.api import result

app = FastAPI()

app.include_router(user.router)
app.include_router(upload.router)
app.include_router(result.router)
