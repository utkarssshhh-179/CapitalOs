from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LedgerDirection(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerEntryType(StrEnum):
    DISBURSEMENT = "disbursement"
    PAYMENT = "payment"
    ACCRUAL = "accrual"
    PENALTY = "penalty"
    FEE = "fee"
    REVERSAL = "reversal"


class LedgerEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ledger_entries"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    loan_id: Mapped[UUID] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    borrower_id: Mapped[UUID] = mapped_column(ForeignKey("borrowers.id"), nullable=False, index=True)
    entry_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    entry_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=LedgerEntryType.PAYMENT.value,
        server_default=LedgerEntryType.PAYMENT.value,
        index=True,
    )
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=LedgerDirection.DEBIT.value,
        server_default=LedgerDirection.DEBIT.value,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    balance_after: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    reversal_of_id: Mapped[UUID | None] = mapped_column(ForeignKey("ledger_entries.id"), nullable=True, index=True)
    related_payment_id: Mapped[UUID | None] = mapped_column(ForeignKey("payments.id"), nullable=True, index=True)
    related_collection_id: Mapped[UUID | None] = mapped_column(ForeignKey("collections.id"), nullable=True, index=True)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
