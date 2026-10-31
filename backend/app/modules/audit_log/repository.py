from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> AuditLog:
        record = AuditLog(**data)
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_by_id(self, log_id: UUID) -> AuditLog | None:
        result = await self.session.execute(select(AuditLog).where(AuditLog.id == log_id))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog).where(AuditLog.organization_id == organization_id).order_by(AuditLog.occurred_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[AuditLog]:
        result = await self.session.execute(select(AuditLog).order_by(AuditLog.occurred_at.desc()))
        return list(result.scalars().all())

    async def update(self, record: AuditLog, data: dict[str, Any]) -> AuditLog:
        for field, value in data.items():
            setattr(record, field, value)
        await self.session.flush()
        return record
