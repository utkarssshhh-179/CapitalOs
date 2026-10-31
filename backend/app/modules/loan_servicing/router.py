from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.loan_servicing.repository import LoanServicingRepository
from app.modules.loan_servicing.schemas import LoanServicingCreate, LoanServicingResponse, LoanServicingUpdate
from app.modules.loan_servicing.service import LoanServicingService

router = APIRouter(prefix="/loan-servicing", tags=["loan-servicing"])


@router.get("", response_model=list[LoanServicingResponse])
async def list_loan_servicing(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[LoanServicingResponse]:
    service = LoanServicingService(LoanServicingRepository(session))
    return await service.list_servicing_records(organization_id)


@router.get("/{servicing_id}", response_model=LoanServicingResponse)
async def get_loan_servicing(
    servicing_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanServicingResponse:
    service = LoanServicingService(LoanServicingRepository(session))
    return await service.get_servicing_record(servicing_id)


@router.get("/loan/{loan_id}", response_model=LoanServicingResponse)
async def get_loan_servicing_by_loan(
    loan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanServicingResponse:
    service = LoanServicingService(LoanServicingRepository(session))
    return await service.get_by_loan_id(loan_id)


@router.post("", response_model=LoanServicingResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_servicing(
    payload: LoanServicingCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanServicingResponse:
    service = LoanServicingService(LoanServicingRepository(session))
    return await service.create_servicing_record(payload)


@router.patch("/{servicing_id}", response_model=LoanServicingResponse)
async def update_loan_servicing(
    servicing_id: UUID,
    payload: LoanServicingUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanServicingResponse:
    service = LoanServicingService(LoanServicingRepository(session))
    return await service.update_servicing_record(servicing_id, payload)
