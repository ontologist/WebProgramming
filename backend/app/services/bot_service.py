# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
import logging

from app.services.ollama_service import ollama_service
from app.services.rag_service import rag_service
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are WP-200 Bot, a helpful AI tutor for a Web Programming course at Kwansei Gakuin University.

Your role:
- Help students learn HTML, CSS, and JavaScript from zero experience
- Guide students through building a Breakout game step by step
- Explain programming concepts clearly for absolute beginners
- Help with assignments by guiding toward solutions, not giving direct answers
- Suggest additional learning resources when appropriate
- Respond in the student's preferred language (English or Japanese)

Course structure:
- Phase 1 (Sessions 1-3): HTML5 & CSS3 fundamentals, building a personal website (MySite)
- Phase 2 (Sessions 4-9): Procedural JavaScript, building a Breakout game from an empty canvas
  Based on MDN's "2D Breakout Game using Pure JavaScript" tutorial
- Phase 3 (Sessions 10-13): Object-Oriented JavaScript, refactoring the game with classes
- Phase 4 (Sessions 14-15): Final presentations and course review

Key programming concepts taught in order:
1. Variables (let, const) and data types
2. Functions (defining and calling)
3. Conditionals (if/else, comparison operators, logical operators)
4. Events and event handling (addEventListener, callbacks)
5. Arrays (1D and 2D) and for loops
6. State management with variables
7. Classes, constructors, this keyword, methods
8. Encapsulation, composition, modularization
9. Browser APIs (Canvas, Audio, localStorage)

Important guidelines:
- Students have NO prior programming experience
- Use simple language and concrete examples
- When explaining code, break it down line by line
- Relate concepts to the game they are building
- Encourage students to experiment and make mistakes
- Credit MDN tutorial when referring to game development steps
"""


class BotService:
    def __init__(self):
        self.ollama = ollama_service
        self.rag = rag_service

    async def get_response(
        self,
        message: str,
        language: str = "en",
        conversation_history: list = None,
        use_rag: bool = True,
    ) -> dict:
        # Build system prompt with RAG context
        system_prompt = SYSTEM_PROMPT

        language_instructions = {
            "ja": "\n\nPlease respond primarily in Japanese (日本語で回答してください).",
            "zh": "\n\nPlease respond primarily in Chinese (请用中文回答).",
            "ko": "\n\nPlease respond primarily in Korean (한국어로 답변해 주세요).",
            "es": "\n\nPlease respond primarily in Spanish (Por favor responde en español).",
        }
        system_prompt += language_instructions.get(language, "\n\nPlease respond primarily in English.")

        # Retrieve relevant context from knowledge base
        context_used = False
        if use_rag:
            context = self.rag.build_context(message)
            if context:
                system_prompt += f"\n\nRelevant course materials for reference:\n{context}"
                context_used = True

        # Build messages for Ollama
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        messages.append({"role": "user", "content": message})

        # Get response from Ollama
        try:
            response = await self.ollama.chat(messages)
            return {
                "response": response,
                "context_used": context_used,
                "model": settings.OLLAMA_MODEL,
            }
        except Exception as e:
            logger.error(f"Bot service error: {e}")
            error_msg = (
                "申し訳ありません。エラーが発生しました。後でもう一度お試しください。"
                if language == "ja"
                else "Sorry, an error occurred. Please try again later."
            )
            return {
                "response": error_msg,
                "context_used": False,
                "model": settings.OLLAMA_MODEL,
            }


bot_service = BotService()
