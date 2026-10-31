from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.borrower import BorrowerStatus


class BorrowerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = None
    pan_number: str | None = None
    aadhaar_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str = "India"
    annual_income: float | None = None
    status: BorrowerStatus = BorrowerStatus.ACTIVE
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BorrowerCreate(BorrowerBase):
    organization_id: UUID | None = None


class BorrowerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    pan_number: str | None = None
    aadhaar_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    annual_income: float | None = None
    status: BorrowerStatus | str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BorrowerResponse(BorrowerBase):
    id: UUID
    organization_id: UUID
    created_at: Any
    updated_at: Any
