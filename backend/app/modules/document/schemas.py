from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=100000)

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    filename: str
    size_bytes: int
    extracted_text: str
    status: str = "processed"

    model_config = ConfigDict(from_attributes=True)
