from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.underwriting.repository import UnderwritingReviewRepository
from app.modules.underwriting.schemas import UnderwritingReviewCreate, UnderwritingReviewResponse, UnderwritingReviewUpdate
from app.modules.underwriting.service import UnderwritingReviewService

router = APIRouter(prefix="/underwriting", tags=["underwriting"])


@router.get("", response_model=list[UnderwritingReviewResponse])
async def list_underwriting_reviews(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[UnderwritingReviewResponse]:
    service = UnderwritingReviewService(UnderwritingReviewRepository(session))
    return await service.list_reviews(organization_id)


@router.get("/{review_id}", response_model=UnderwritingReviewResponse)
async def get_underwriting_review(
    review_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnderwritingReviewResponse:
    service = UnderwritingReviewService(UnderwritingReviewRepository(session))
    return await service.get_review(review_id)


@router.get("/loan/{loan_id}", response_model=UnderwritingReviewResponse)
async def get_underwriting_review_by_loan(
    loan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnderwritingReviewResponse:
    service = UnderwritingReviewService(UnderwritingReviewRepository(session))
    return await service.get_review_by_loan(loan_id)


@router.post("", response_model=UnderwritingReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_underwriting_review(
    payload: UnderwritingReviewCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnderwritingReviewResponse:
    service = UnderwritingReviewService(UnderwritingReviewRepository(session))
    return await service.create_review(payload)


@router.patch("/{review_id}", response_model=UnderwritingReviewResponse)
async def update_underwriting_review(
    review_id: UUID,
    payload: UnderwritingReviewUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnderwritingReviewResponse:
    service = UnderwritingReviewService(UnderwritingReviewRepository(session))
    return await service.update_review(review_id, payload)
