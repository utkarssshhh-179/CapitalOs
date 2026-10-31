from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.loan_schedule import LoanScheduleStatus


class LoanScheduleBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    installment_number: int = Field(..., gt=0)
    due_date: datetime
    principal_component: Decimal = Field(..., ge=0)
    interest_component: Decimal = Field(..., ge=0)
    total_installment: Decimal = Field(..., gt=0)
    status: LoanScheduleStatus = LoanScheduleStatus.SCHEDULED
    paid_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanScheduleCreate(LoanScheduleBase):
    pass


class LoanScheduleUpdate(BaseModel):
    installment_number: int | None = Field(default=None, gt=0)
    due_date: datetime | None = None
    principal_component: Decimal | None = Field(default=None, ge=0)
    interest_component: Decimal | None = Field(default=None, ge=0)
    total_installment: Decimal | None = Field(default=None, gt=0)
    status: LoanScheduleStatus | str | None = None
    paid_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoanScheduleResponse(LoanScheduleBase):
    id: UUID
    created_at: Any
    updated_at: Any
