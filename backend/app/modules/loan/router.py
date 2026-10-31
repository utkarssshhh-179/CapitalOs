from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.loan.repository import LoanRepository
from app.modules.loan.schemas import LoanCreate, LoanResponse, LoanUpdate
from app.modules.loan.service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=list[LoanResponse])
async def list_loans(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[LoanResponse]:
    service = LoanService(LoanRepository(session))
    return await service.list_loans(organization_id)


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanResponse:
    service = LoanService(LoanRepository(session))
    return await service.get_loan(loan_id)


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    payload: LoanCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanResponse:
    service = LoanService(LoanRepository(session))
    return await service.create_loan(payload)


@router.patch("/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: UUID,
    payload: LoanUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanResponse:
    service = LoanService(LoanRepository(session))
    return await service.update_loan(loan_id, payload)


@router.delete("/{loan_id}", response_model=LoanResponse)
async def close_loan(
    loan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LoanResponse:
    service = LoanService(LoanRepository(session))
    return await service.mark_loan_closed(loan_id)
