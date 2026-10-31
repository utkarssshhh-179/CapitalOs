from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LoanStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DISBURSED = "disbursed"
    ACTIVE = "active"
    CLOSED = "closed"
    DEFAULTED = "defaulted"


class Loan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "loans"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    borrower_id: Mapped[UUID] = mapped_column(ForeignKey("borrowers.id"), nullable=False, index=True)
    investor_id: Mapped[UUID] = mapped_column(ForeignKey("investors.id"), nullable=False, index=True)
    loan_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    principal_amount: Mapped[float] = mapped_column(nullable=False)
    interest_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    tenure_months: Mapped[int] = mapped_column(nullable=False)
    purpose: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=LoanStatus.PENDING.value,
        server_default=LoanStatus.PENDING.value,
        index=True,
    )
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    maturity_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
