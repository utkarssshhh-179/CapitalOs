from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.core.money import to_money
from app.models.underwriting_review import UnderwritingReview, UnderwritingStatus
from app.modules.underwriting.repository import UnderwritingReviewRepository
from app.modules.underwriting.schemas import UnderwritingReviewCreate, UnderwritingReviewUpdate


class UnderwritingReviewService:
    def __init__(self, repository: UnderwritingReviewRepository) -> None:
        self.repository = repository

    async def create_review(self, payload: UnderwritingReviewCreate) -> UnderwritingReview:
        existing = await self.repository.get_by_loan_id(payload.loan_id)
        if existing is not None:
            raise ConflictError("Underwriting review already exists for this loan", details={"loan_id": str(payload.loan_id)})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        if data.get("recommended_amount") is not None:
            data["recommended_amount"] = to_money(data["recommended_amount"])
        if data.get("approved_amount") is not None:
            data["approved_amount"] = to_money(data["approved_amount"])
        data.setdefault("status", UnderwritingStatus.PENDING.value)
        return await self.repository.create(data)

    async def list_reviews(self, organization_id: UUID | None = None) -> list[UnderwritingReview]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_review(self, review_id: UUID) -> UnderwritingReview:
        review = await self.repository.get_by_id(review_id)
        if review is None:
            raise NotFoundError("Underwriting review not found", details={"id": str(review_id)})
        return review

    async def get_review_by_loan(self, loan_id: UUID) -> UnderwritingReview:
        review = await self.repository.get_by_loan_id(loan_id)
        if review is None:
            raise NotFoundError("Underwriting review not found", details={"loan_id": str(loan_id)})
        return review

    async def update_review(self, review_id: UUID, payload: UnderwritingReviewUpdate) -> UnderwritingReview:
        review = await self.get_review(review_id)
        data = payload.model_dump(exclude_unset=True)

        if "recommended_amount" in data and data["recommended_amount"] is not None:
            data["recommended_amount"] = to_money(data["recommended_amount"])
        if "approved_amount" in data and data["approved_amount"] is not None:
            data["approved_amount"] = to_money(data["approved_amount"])
        if "status" in data and data["status"] is not None:
            data["status"] = UnderwritingStatus(data["status"]).value
        if "reviewed_at" in data and data["reviewed_at"] is None:
            data["reviewed_at"] = datetime.now()

        return await self.repository.update(review, data)

    async def approve_review(
        self,
        review_id: UUID,
        *,
        reviewer_user_id: UUID,
        approved_amount: Decimal | int | str,
        rationale: str | None = None,
    ) -> UnderwritingReview:
        review = await self.get_review(review_id)
        data = {
            "reviewer_user_id": reviewer_user_id,
            "approved_amount": to_money(approved_amount),
            "status": UnderwritingStatus.APPROVED.value,
            "reviewed_at": datetime.now(),
            "rationale": rationale or review.rationale,
        }
        return await self.repository.update(review, data)
