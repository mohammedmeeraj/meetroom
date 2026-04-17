from fastapi import FastAPI, Depends
from typing import Annotated
from .dependencies import get_settings
from pydantic_settings import BaseSettings
from app.routers import auth, rooms
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Anonymous video meeting backend",
    version="1.0.0",
)


# ---CORS-------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---Routers----------------------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")

@app.get("/")
def root(settings: Annotated[BaseSettings, Depends(get_settings)]):
    return {"status":"ok", "app":settings.APP_NAME}

@app.get("/health")
def health():
    return {"status": "healthy"}