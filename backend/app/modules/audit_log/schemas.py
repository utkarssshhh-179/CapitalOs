from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.audit_log import AuditAction


class AuditLogBase(BaseModel):
    organization_id: UUID
    actor_user_id: UUID | None = None
    entity_type: str = Field(..., min_length=2, max_length=50)
    entity_id: str = Field(..., min_length=1, max_length=80)
    action: AuditAction = AuditAction.CREATE
    summary: str | None = Field(default=None, max_length=255)
    details: str | None = Field(default=None, max_length=2000)
    ip_address: str | None = Field(default=None, max_length=50)
    user_agent: str | None = Field(default=None, max_length=500)
    occurred_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    actor_user_id: UUID | None = None
    entity_type: str | None = Field(default=None, min_length=2, max_length=50)
    entity_id: str | None = Field(default=None, min_length=1, max_length=80)
    action: AuditAction | str | None = None
    summary: str | None = Field(default=None, max_length=255)
    details: str | None = Field(default=None, max_length=2000)
    ip_address: str | None = Field(default=None, max_length=50)
    user_agent: str | None = Field(default=None, max_length=500)
    occurred_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(AuditLogBase):
    id: UUID
    created_at: Any
    updated_at: Any
