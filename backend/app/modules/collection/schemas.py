from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.collection import CollectionStatus


class CollectionBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    borrower_id: UUID
    case_number: str = Field(..., min_length=3, max_length=50)
    status: CollectionStatus = CollectionStatus.OPEN
    assigned_to: str | None = None
    follow_up_date: datetime | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    case_number: str | None = Field(default=None, min_length=3, max_length=50)
    status: CollectionStatus | str | None = None
    assigned_to: str | None = None
    follow_up_date: datetime | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CollectionResponse(CollectionBase):
    id: UUID
    created_at: Any
    updated_at: Any
