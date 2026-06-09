# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
import logging
from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from app.services.bot_service import bot_service
from app.services.ollama_service import ollama_service
from app.services.rag_service import rag_service
from app.services import db_service, auth_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str = "en"
    conversation_history: list = []
    use_rag: bool = True


class ChatResponse(BaseModel):
    response: str
    user_id: str
    language: str
    context_used: bool
    model: str
    persisted: bool = False
    conversation_id: Optional[int] = None


def _bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(default=None)):
    result = await bot_service.get_response(
        message=request.message,
        language=request.language,
        conversation_history=request.conversation_history,
        use_rag=request.use_rag,
    )

    persisted = False
    conversation_id = None

    session = auth_service.validate_session(_bearer_token(authorization))
    if session:
        try:
            conversation_id = db_service.get_or_create_active_conversation(
                handle=session["handle"], language=request.language,
            )
            db_service.append_message(conversation_id, "user", request.message)
            db_service.append_message(conversation_id, "assistant", result["response"])
            persisted = True
        except Exception as e:
            logger.exception(f"Failed to persist chat for {session['handle']}: {e}")

    return ChatResponse(
        response=result["response"],
        user_id=request.user_id,
        language=request.language,
        context_used=result["context_used"],
        model=result["model"],
        persisted=persisted,
        conversation_id=conversation_id,
    )


@router.get("/health")
async def health():
    ollama_ok = await ollama_service.health_check()
    rag_info = rag_service.get_collection_info()
    models = await ollama_service.list_models() if ollama_ok else []

    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": {"connected": ollama_ok, "model": settings.OLLAMA_MODEL, "available_models": models},
        "rag": rag_info,
        "course": settings.COURSE_ID,
    }


@router.get("/test")
async def test():
    result = await bot_service.get_response(
        message="What is this course about?",
        language="en",
        use_rag=True,
    )
    return {"test_response": result["response"][:200], "model": result["model"]}
