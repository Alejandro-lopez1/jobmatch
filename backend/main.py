from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routers import cv, jobs, sheets

app = FastAPI(
    title="JobMatch API",
    description="Sistema de búsqueda de empleo con matching inteligente",
    version="0.1.0",
)

app.include_router(cv.router)
app.include_router(jobs.router)
app.include_router(sheets.router)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/")
async def root():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "JobMatch API - Documentation at /docs"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
