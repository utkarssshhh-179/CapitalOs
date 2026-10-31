from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.underwriting_review import UnderwritingReview


class UnderwritingReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> UnderwritingReview:
        review = UnderwritingReview(**data)
        self.session.add(review)
        await self.session.flush()
        return review

    async def get_by_id(self, review_id: UUID) -> UnderwritingReview | None:
        result = await self.session.execute(select(UnderwritingReview).where(UnderwritingReview.id == review_id))
        return result.scalar_one_or_none()

    async def get_by_loan_id(self, loan_id: UUID) -> UnderwritingReview | None:
        result = await self.session.execute(select(UnderwritingReview).where(UnderwritingReview.loan_id == loan_id))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[UnderwritingReview]:
        result = await self.session.execute(
            select(UnderwritingReview)
            .where(UnderwritingReview.organization_id == organization_id)
            .order_by(UnderwritingReview.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[UnderwritingReview]:
        result = await self.session.execute(select(UnderwritingReview).order_by(UnderwritingReview.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, review: UnderwritingReview, data: dict[str, Any]) -> UnderwritingReview:
        for field, value in data.items():
            setattr(review, field, value)
        await self.session.flush()
        return review
