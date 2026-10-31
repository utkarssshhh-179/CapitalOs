from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ledger import LedgerDirection, LedgerEntryType


class LedgerEntryBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    borrower_id: UUID
    entry_number: str = Field(..., min_length=3, max_length=50)
    entry_type: LedgerEntryType = LedgerEntryType.PAYMENT
    direction: LedgerDirection = LedgerDirection.DEBIT
    amount: Decimal = Field(..., gt=0)
    balance_after: Decimal | None = None
    reversal_of_id: UUID | None = None
    related_payment_id: UUID | None = None
    related_collection_id: UUID | None = None
    effective_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryCreate(LedgerEntryBase):
    pass


class LedgerEntryUpdate(BaseModel):
    entry_number: str | None = Field(default=None, min_length=3, max_length=50)
    entry_type: LedgerEntryType | str | None = None
    direction: LedgerDirection | str | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    balance_after: Decimal | None = None
    reversal_of_id: UUID | None = None
    related_payment_id: UUID | None = None
    related_collection_id: UUID | None = None
    effective_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryResponse(LedgerEntryBase):
    id: UUID
    created_at: Any
    updated_at: Any
