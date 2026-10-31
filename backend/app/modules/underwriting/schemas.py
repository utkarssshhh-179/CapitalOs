from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.underwriting_review import UnderwritingStatus


class UnderwritingReviewBase(BaseModel):
    organization_id: UUID
    loan_id: UUID
    reviewer_user_id: UUID | None = None
    status: UnderwritingStatus = UnderwritingStatus.PENDING
    risk_score: int = Field(default=0, ge=0, le=100)
    risk_band: str | None = None
    recommended_amount: Decimal | None = Field(default=None, ge=0)
    approved_amount: Decimal | None = Field(default=None, ge=0)
    rationale: str | None = None
    reviewed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UnderwritingReviewCreate(UnderwritingReviewBase):
    pass


class UnderwritingReviewUpdate(BaseModel):
    reviewer_user_id: UUID | None = None
    status: UnderwritingStatus | str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_band: str | None = None
    recommended_amount: Decimal | None = Field(default=None, ge=0)
    approved_amount: Decimal | None = Field(default=None, ge=0)
    rationale: str | None = None
    reviewed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UnderwritingReviewResponse(UnderwritingReviewBase):
    id: UUID
    created_at: Any
    updated_at: Any
