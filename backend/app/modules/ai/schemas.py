from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AIRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)
    context: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AIResponse(BaseModel):
    answer: str
    model: str = "capitalos-ai"
    prompt_tokens: int = 0
    completion_tokens: int = 0

    model_config = ConfigDict(from_attributes=True)
