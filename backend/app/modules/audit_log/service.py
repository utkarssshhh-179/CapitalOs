from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.audit_log import AuditAction, AuditLog
from app.modules.audit_log.repository import AuditLogRepository
from app.modules.audit_log.schemas import AuditLogCreate, AuditLogUpdate


class AuditLogService:
    def __init__(self, repository: AuditLogRepository) -> None:
        self.repository = repository

    async def create_log(self, payload: AuditLogCreate) -> AuditLog:
        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data.setdefault("action", AuditAction.CREATE.value)
        data.setdefault("occurred_at", datetime.now())
        return await self.repository.create(data)

    async def list_logs(self, organization_id: UUID | None = None) -> list[AuditLog]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_log(self, log_id: UUID) -> AuditLog:
        log = await self.repository.get_by_id(log_id)
        if log is None:
            raise NotFoundError("Audit log not found", details={"id": str(log_id)})
        return log

    async def update_log(self, log_id: UUID, payload: AuditLogUpdate) -> AuditLog:
        log = await self.get_log(log_id)
        data = payload.model_dump(exclude_unset=True)
        if "action" in data and data["action"] is not None:
            data["action"] = AuditAction(data["action"]).value
        return await self.repository.update(log, data)
