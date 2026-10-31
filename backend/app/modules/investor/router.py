from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.investor.repository import InvestorRepository
from app.modules.investor.schemas import InvestorCreate, InvestorResponse, InvestorUpdate
from app.modules.investor.service import InvestorService

router = APIRouter(prefix="/investors", tags=["investors"])


@router.get("", response_model=list[InvestorResponse])
async def list_investors(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[InvestorResponse]:
    service = InvestorService(InvestorRepository(session))
    return await service.list_investors(organization_id)


@router.get("/{investor_id}", response_model=InvestorResponse)
async def get_investor(
    investor_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvestorResponse:
    service = InvestorService(InvestorRepository(session))
    return await service.get_investor(investor_id)


@router.post("", response_model=InvestorResponse, status_code=status.HTTP_201_CREATED)
async def create_investor(
    payload: InvestorCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvestorResponse:
    service = InvestorService(InvestorRepository(session))
    return await service.create_investor(payload)


@router.patch("/{investor_id}", response_model=InvestorResponse)
async def update_investor(
    investor_id: UUID,
    payload: InvestorUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvestorResponse:
    service = InvestorService(InvestorRepository(session))
    return await service.update_investor(investor_id, payload)


@router.delete("/{investor_id}", response_model=InvestorResponse)
async def archive_investor(
    investor_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvestorResponse:
    service = InvestorService(InvestorRepository(session))
    return await service.archive_investor(investor_id)
