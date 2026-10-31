from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UnderwritingStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    CONDITIONAL = "conditional"


class UnderwritingReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "underwriting_reviews"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    loan_id: Mapped[UUID] = mapped_column(ForeignKey("loans.id"), nullable=False, unique=True, index=True)
    reviewer_user_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UnderwritingStatus.PENDING.value,
        server_default=UnderwritingStatus.PENDING.value,
        index=True,
    )
    risk_score: Mapped[int] = mapped_column(nullable=False, default=0, index=True)
    risk_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recommended_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    approved_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    rationale: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
