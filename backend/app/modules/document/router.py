from __future__ import annotations

from fastapi import APIRouter

from app.modules.document.schemas import DocumentRequest, DocumentResponse
from app.modules.document.service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/process", response_model=DocumentResponse)
async def process_document(payload: DocumentRequest) -> DocumentResponse:
    service = DocumentService()
    return await service.process_document(payload)
