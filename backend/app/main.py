from fastapi import FastAPI, Depends
from typing import Annotated
from .dependencies import get_settings
from pydantic_settings import BaseSettings
from app.routers import auth


app = FastAPI(
    title="MeetRoom",
    description="Anonymous video meeting backend",
    version="1.0.0",
)

# ---Routers----------------------------------------------------------------
app.include_router(auth.router, prefix="/api")

@app.get("/")
async def root(settings: Annotated[BaseSettings, Depends(get_settings)]):
    return {"status":"ok", "app":settings.APP_NAME}

@app.get("/health")
async def health():
    return {"status": "healthy"}