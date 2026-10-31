from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.loan_schedule.repository import LoanScheduleRepository
from app.modules.loan_schedule.schemas import LoanScheduleCreate, LoanScheduleResponse, LoanScheduleUpdate
from app.modules.loan_schedule.service import LoanScheduleService

router = APIRouter(prefix="/loan-schedules", tags=["loan-schedules"])


@router.get("", response_model=list[LoanScheduleResponse])
async def list_loan_schedules(
    session: Annotated[AsyncSession, Depends(get_session)],
    loan_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> list[LoanScheduleResponse]:
    service = LoanScheduleService(LoanScheduleRepository(session))
    return await service.list_schedule_entries(loan_id=loan_id, organization_id=organization_id)


@router.get("/{schedule_id}", response_model=LoanScheduleResponse)
async def get_loan_schedule(
    schedule_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanScheduleResponse:
    service = LoanScheduleService(LoanScheduleRepository(session))
    return await service.get_schedule_entry(schedule_id)


@router.post("", response_model=LoanScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_schedule(
    payload: LoanScheduleCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanScheduleResponse:
    service = LoanScheduleService(LoanScheduleRepository(session))
    return await service.create_schedule_entry(payload)


@router.patch("/{schedule_id}", response_model=LoanScheduleResponse)
async def update_loan_schedule(
    schedule_id: UUID,
    payload: LoanScheduleUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanScheduleResponse:
    service = LoanScheduleService(LoanScheduleRepository(session))
    return await service.update_schedule_entry(schedule_id, payload)
