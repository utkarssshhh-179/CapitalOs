from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.investor import InvestorStatus


class InvestorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str = "India"
    investment_capacity: float | None = None
    status: InvestorStatus = InvestorStatus.ACTIVE
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InvestorCreate(InvestorBase):
    organization_id: UUID | None = None


class InvestorUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    investment_capacity: float | None = None
    status: InvestorStatus | str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InvestorResponse(InvestorBase):
    id: UUID
    organization_id: UUID
    created_at: Any
    updated_at: Any
