from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.organization import OrganizationStatus


class OrganizationBase(BaseModel):
    legal_name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    gst_number: str | None = Field(default=None, max_length=50)
    pan_number: str | None = Field(default=None, max_length=20)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=255)
    timezone: str = "Asia/Kolkata"
    currency: str = "INR"
    country: str = "India"
    logo_url: str | None = Field(default=None, max_length=500)
    status: OrganizationStatus = OrganizationStatus.ACTIVE

    model_config = ConfigDict(use_enum_values=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    legal_name: str | None = Field(default=None, min_length=1, max_length=255)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    gst_number: str | None = Field(default=None, max_length=50)
    pan_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=255)
    timezone: str | None = None
    currency: str | None = None
    country: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)
    status: OrganizationStatus | None = None

    model_config = ConfigDict(use_enum_values=True)


class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
