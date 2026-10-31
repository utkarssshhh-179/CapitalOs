from __future__ import annotations

from app.modules.document.schemas import DocumentRequest, DocumentResponse


class DocumentService:
    async def process_document(self, payload: DocumentRequest) -> DocumentResponse:
        text = payload.content.strip()
        if not text:
            raise ValueError("Document content cannot be empty")

        return DocumentResponse(
            filename=payload.filename,
            size_bytes=len(payload.content.encode("utf-8")),
            extracted_text=text[:2000],
        )
