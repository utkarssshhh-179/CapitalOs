from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.loan_servicing import LoanServicingStatus


class LoanServicingBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    status: LoanServicingStatus = LoanServicingStatus.ACTIVE
    principal_outstanding: Decimal = Field(..., ge=0)
    interest_outstanding: Decimal = Field(..., ge=0)
    total_outstanding: Decimal = Field(..., ge=0)
    next_due_date: datetime | None = None
    days_past_due: int = Field(default=0, ge=0)
    last_payment_amount: Decimal | None = Field(default=None, ge=0)
    last_payment_date: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanServicingCreate(LoanServicingBase):
    pass


class LoanServicingUpdate(BaseModel):
    status: LoanServicingStatus | str | None = None
    principal_outstanding: Decimal | None = Field(default=None, ge=0)
    interest_outstanding: Decimal | None = Field(default=None, ge=0)
    total_outstanding: Decimal | None = Field(default=None, ge=0)
    next_due_date: datetime | None = None
    days_past_due: int | None = Field(default=None, ge=0)
    last_payment_amount: Decimal | None = Field(default=None, ge=0)
    last_payment_date: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanServicingResponse(LoanServicingBase):
    id: UUID
    created_at: Any
    updated_at: Any
