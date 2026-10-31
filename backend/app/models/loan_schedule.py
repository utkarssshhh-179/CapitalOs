from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LoanScheduleStatus(StrEnum):
    SCHEDULED = "scheduled"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class LoanSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "loan_schedules"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    loan_id: Mapped[UUID] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    installment_number: Mapped[int] = mapped_column(nullable=False, index=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    principal_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_installment: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=LoanScheduleStatus.SCHEDULED.value,
        server_default=LoanScheduleStatus.SCHEDULED.value,
        index=True,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
