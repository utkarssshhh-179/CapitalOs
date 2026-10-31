from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.underwriting_review import UnderwritingReview, UnderwritingStatus
from app.modules.underwriting.schemas import UnderwritingReviewCreate, UnderwritingReviewUpdate
from app.modules.underwriting.service import UnderwritingReviewService


class FakeUnderwritingRepository:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, UnderwritingReview] = {}

    async def create(self, data: dict[str, object]) -> UnderwritingReview:
        record = UnderwritingReview(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.id] = record
        return record

    async def get_by_id(self, review_id: uuid.UUID) -> UnderwritingReview | None:
        return self.items.get(review_id)

    async def get_by_loan_id(self, loan_id: uuid.UUID) -> UnderwritingReview | None:
        for record in self.items.values():
            if record.loan_id == loan_id:
                return record
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[UnderwritingReview]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[UnderwritingReview]:
        return list(self.items.values())

    async def update(self, review: UnderwritingReview, data: dict[str, object]) -> UnderwritingReview:
        for key, value in data.items():
            setattr(review, key, value)
        review.updated_at = datetime.now(UTC)
        return review


@pytest.mark.asyncio
async def test_create_review_succeeds() -> None:
    service = UnderwritingReviewService(FakeUnderwritingRepository())
    loan_id = uuid.uuid4()

    review = await service.create_review(
        UnderwritingReviewCreate(
            organization_id=uuid.uuid4(),
            loan_id=loan_id,
            risk_score=82,
            risk_band="low",
            recommended_amount=Decimal("12000.00"),
            rationale="Strong applicant profile",
        )
    )

    assert review.loan_id == loan_id
    assert review.status == UnderwritingStatus.PENDING.value
    assert review.risk_score == 82


@pytest.mark.asyncio
async def test_create_review_rejects_duplicate_loan() -> None:
    repository = FakeUnderwritingRepository()
    service = UnderwritingReviewService(repository)
    loan_id = uuid.uuid4()

    await service.create_review(
        UnderwritingReviewCreate(
            organization_id=uuid.uuid4(),
            loan_id=loan_id,
            risk_score=75,
            recommended_amount=Decimal("8000.00"),
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_review(
            UnderwritingReviewCreate(
                organization_id=uuid.uuid4(),
                loan_id=loan_id,
                risk_score=60,
                recommended_amount=Decimal("5000.00"),
            )
        )


@pytest.mark.asyncio
async def test_approve_review_sets_approval_details() -> None:
    repository = FakeUnderwritingRepository()
    service = UnderwritingReviewService(repository)

    review = await service.create_review(
        UnderwritingReviewCreate(
            organization_id=uuid.uuid4(),
            loan_id=uuid.uuid4(),
            risk_score=90,
            recommended_amount=Decimal("20000.00"),
        )
    )

    approved = await service.approve_review(review.id, reviewer_user_id=uuid.uuid4(), approved_amount=Decimal("18000.00"))

    assert approved.status == UnderwritingStatus.APPROVED.value
    assert approved.approved_amount == Decimal("18000.00")


@pytest.mark.asyncio
async def test_get_review_by_loan_not_found() -> None:
    service = UnderwritingReviewService(FakeUnderwritingRepository())

    with pytest.raises(NotFoundError, match="not found"):
        await service.get_review_by_loan(uuid.uuid4())
