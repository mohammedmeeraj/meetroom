from fastapi import FastAPI, Depends
from typing import Annotated
from . import config
from functools import lru_cache

@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI(
    title=Annotated[config.Settings, Depends(get_settings)],
    description="Anonymous video meeting backend",
    version="1.0.0",
)

@app.get("/")
async def root(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {"status":"ok", "app":settings.app_name}

@app.get("/health")
async def health():
    return {"status": "healthy"}