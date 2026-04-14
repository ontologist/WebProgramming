# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
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

# Seed instructor account
from app.services.db_service import upsert_student
upsert_student(
    handle="bhw95799",
    student_id="INSTRUCTOR",
    email="bhw95799@kwansei.ac.jp",
    kanji_name="ティヘリノ Ｙ．Ａ．",
    romaji_name="TIJERINO YURI ADRIAN",
)
logger.info("Instructor account seeded: bhw95799")

# Serve instructor dashboard static files
dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="dashboard")

# Serve course site from docs/ folder as the root site
# This must be mounted LAST because it catches all unmatched routes
docs_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
if os.path.exists(docs_path):
    app.mount("/", StaticFiles(directory=docs_path, html=True), name="course-site")
    logger.info(f"Serving course site from {docs_path}")
else:
    # Fallback: if docs/ not found relative to backend, try COURSE_SITE_PATH from config
    @app.get("/")
    async def root():
        return {
            "course": settings.COURSE_NAME,
            "course_site": "docs/ not found - set COURSE_SITE_PATH in .env",
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
