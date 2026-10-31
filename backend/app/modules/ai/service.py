from __future__ import annotations

from app.modules.ai.schemas import AIRequest, AIResponse


class AIService:
    async def generate_answer(self, payload: AIRequest) -> AIResponse:
        prompt = payload.prompt.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        context_snippet = payload.context.strip() if payload.context else ""
        if context_snippet:
            answer = f"Context-aware response for: {prompt}\n\nContext: {context_snippet}"
        else:
            answer = f"AI assistant response for: {prompt}"

        return AIResponse(
            answer=answer,
            model="capitalos-ai",
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(answer.split()),
        )
