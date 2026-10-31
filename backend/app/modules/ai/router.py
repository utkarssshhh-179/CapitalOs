from __future__ import annotations

from fastapi import APIRouter

from app.modules.ai.schemas import AIRequest, AIResponse
from app.modules.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(payload: AIRequest) -> AIResponse:
    service = AIService()
    return await service.generate_answer(payload)
