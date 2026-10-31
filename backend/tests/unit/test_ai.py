from __future__ import annotations

import pytest

from app.modules.ai.schemas import AIRequest
from app.modules.ai.service import AIService


@pytest.mark.asyncio
async def test_ai_service_returns_answer_with_context() -> None:
    service = AIService()
    response = await service.generate_answer(
        AIRequest(prompt="Summarize the borrower profile", context="Borrower is a salaried professional with verified income.")
    )

    assert response.answer.startswith("Context-aware response for: Summarize the borrower profile")
    assert response.model == "capitalos-ai"
    assert response.prompt_tokens > 0
    assert response.completion_tokens > 0
