# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.bot_service import bot_service
from app.services.ollama_service import ollama_service
from app.services.rag_service import rag_service
from app.core.config import settings

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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await bot_service.get_response(
        message=request.message,
        language=request.language,
        conversation_history=request.conversation_history,
        use_rag=request.use_rag,
    )

    return ChatResponse(
        response=result["response"],
        user_id=request.user_id,
        language=request.language,
        context_used=result["context_used"],
        model=result["model"],
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
