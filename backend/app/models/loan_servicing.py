from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LoanServicingStatus(StrEnum):
    ACTIVE = "active"
    CURRENT = "current"
    DELINQUENT = "delinquent"
    DEFAULTED = "defaulted"
    CLOSED = "closed"
    RESTRUCTURED = "restructured"


class LoanServicing(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "loan_servicing"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    loan_id: Mapped[UUID] = mapped_column(ForeignKey("loans.id"), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=LoanServicingStatus.ACTIVE.value,
        server_default=LoanServicingStatus.ACTIVE.value,
        index=True,
    )
    principal_outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    interest_outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    total_outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    next_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    days_past_due: Mapped[int] = mapped_column(nullable=False, default=0, index=True)
    last_payment_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    last_payment_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
