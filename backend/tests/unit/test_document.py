from __future__ import annotations

import pytest

from app.modules.document.schemas import DocumentRequest
from app.modules.document.service import DocumentService


@pytest.mark.asyncio
async def test_document_service_extracts_text_snippet() -> None:
    service = DocumentService()
    response = await service.process_document(
        DocumentRequest(
            filename="borrower_id_proof.pdf",
            content="Borrower Name: Raj Verma\nIncome: Rs. 1,20,000\nLoan Purpose: Home Improvement",
        )
    )

    assert response.filename == "borrower_id_proof.pdf"
    assert response.size_bytes > 0
    assert "Raj Verma" in response.extracted_text
    assert response.status == "processed"
