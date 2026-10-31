from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    borrower_id: UUID
    payment_number: str = Field(..., min_length=3, max_length=50)
    amount: float = Field(..., gt=0)
    due_date: datetime | None = None
    paid_at: datetime | None = None
    payment_mode: str = "bank_transfer"
    status: PaymentStatus = PaymentStatus.PENDING
    reference_code: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_number: str | None = Field(default=None, min_length=3, max_length=50)
    amount: float | None = Field(default=None, gt=0)
    due_date: datetime | None = None
    paid_at: datetime | None = None
    payment_mode: str | None = None
    status: PaymentStatus | str | None = None
    reference_code: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(PaymentBase):
    id: UUID
    created_at: Any
    updated_at: Any
