# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# Unauthorized copying, modification, or distribution of this file is prohibited.
import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import chat, submissions, instructor, auth
from app.core.config import settings

# Logging
os.makedirs(os.path.dirname(settings.LOG_FILE) if os.path.dirname(settings.LOG_FILE) else "logs", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE),
    ],
)
logger = logging.getLogger(__name__)

# App
app = FastAPI(
    title=f"{settings.COURSE_NAME} Bot API",
    description="Backend API for WP-200 Web Programming course bot, assignment submission, and grading",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(instructor.router, prefix="/api/instructor", tags=["Instructor"])

# Serve instructor dashboard static files
dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="dashboard")


@app.get("/")
async def root():
    return {
        "course": settings.COURSE_NAME,
        "api_docs": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/api/health")
async def health():
    from app.services.ollama_service import ollama_service
    from app.services.rag_service import rag_service
    from app.services.db_service import get_db_info

    ollama_ok = await ollama_service.health_check()
    rag_info = rag_service.get_collection_info()
    db_info = get_db_info()

    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": {"connected": ollama_ok, "model": settings.OLLAMA_MODEL},
        "rag": rag_info,
        "database": db_info,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True,
    )
