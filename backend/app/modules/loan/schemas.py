from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.loan import LoanStatus


class LoanBase(BaseModel):
    organization_id: UUID
    borrower_id: UUID
    investor_id: UUID
    loan_number: str = Field(..., min_length=3, max_length=50)
    principal_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0)
    tenure_months: int = Field(..., gt=0)
    purpose: str | None = None
    status: LoanStatus = LoanStatus.PENDING
    disbursed_at: datetime | None = None
    maturity_date: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    loan_number: str | None = Field(default=None, min_length=3, max_length=50)
    principal_amount: float | None = Field(default=None, gt=0)
    interest_rate: float | None = Field(default=None, ge=0)
    tenure_months: int | None = Field(default=None, gt=0)
    purpose: str | None = None
    status: LoanStatus | str | None = None
    disbursed_at: datetime | None = None
    maturity_date: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanResponse(LoanBase):
    id: UUID
    created_at: Any
    updated_at: Any
