from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.audit_log.repository import AuditLogRepository
from app.modules.audit_log.schemas import AuditLogCreate, AuditLogResponse, AuditLogUpdate
from app.modules.audit_log.service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[AuditLogResponse]:
    service = AuditLogService(AuditLogRepository(session))
    return await service.list_logs(organization_id)


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditLogResponse:
    service = AuditLogService(AuditLogRepository(session))
    return await service.get_log(log_id)


@router.post("", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    payload: AuditLogCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditLogResponse:
    service = AuditLogService(AuditLogRepository(session))
    return await service.create_log(payload)


@router.patch("/{log_id}", response_model=AuditLogResponse)
async def update_audit_log(
    log_id: UUID,
    payload: AuditLogUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditLogResponse:
    service = AuditLogService(AuditLogRepository(session))
    return await service.update_log(log_id, payload)
