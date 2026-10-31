from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.models.audit_log import AuditAction, AuditLog
from app.modules.audit_log.schemas import AuditLogCreate
from app.modules.audit_log.service import AuditLogService


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, AuditLog] = {}

    async def create(self, data: dict[str, object]) -> AuditLog:
        record = AuditLog(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.id] = record
        return record

    async def get_by_id(self, log_id: uuid.UUID) -> AuditLog | None:
        return self.items.get(log_id)

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[AuditLog]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[AuditLog]:
        return list(self.items.values())

    async def update(self, record: AuditLog, data: dict[str, object]) -> AuditLog:
        for key, value in data.items():
            setattr(record, key, value)
        record.updated_at = datetime.now(UTC)
        return record


@pytest.mark.asyncio
async def test_create_audit_log_succeeds() -> None:
    service = AuditLogService(FakeAuditLogRepository())

    log = await service.create_log(
        AuditLogCreate(
            organization_id=uuid.uuid4(),
            actor_user_id=uuid.uuid4(),
            entity_type="loan",
            entity_id="LOAN-1001",
            action=AuditAction.APPROVE,
            summary="Loan approved",
            details="Approval performed by reviewer",
            ip_address="127.0.0.1",
        )
    )

    assert log.action == AuditAction.APPROVE.value
    assert log.entity_type == "loan"
    assert log.summary == "Loan approved"


@pytest.mark.asyncio
async def test_list_logs_by_organization() -> None:
    repository = FakeAuditLogRepository()
    service = AuditLogService(repository)
    organization_id = uuid.uuid4()

    await service.create_log(
        AuditLogCreate(
            organization_id=organization_id,
            entity_type="payment",
            entity_id="PAY-01",
            action=AuditAction.PAYMENT,
            summary="Payment recorded",
        )
    )

    logs = await service.list_logs(organization_id)

    assert len(logs) == 1
    assert logs[0].organization_id == organization_id
    assert logs[0].action == AuditAction.PAYMENT.value
