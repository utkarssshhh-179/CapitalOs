from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.borrower.repository import BorrowerRepository
from app.modules.borrower.schemas import BorrowerCreate, BorrowerResponse, BorrowerUpdate
from app.modules.borrower.service import BorrowerService

router = APIRouter(prefix="/borrowers", tags=["borrowers"])


@router.get("", response_model=list[BorrowerResponse])
async def list_borrowers(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[BorrowerResponse]:
    service = BorrowerService(BorrowerRepository(session))
    return await service.list_borrowers(organization_id)


@router.get("/{borrower_id}", response_model=BorrowerResponse)
async def get_borrower(
    borrower_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BorrowerResponse:
    service = BorrowerService(BorrowerRepository(session))
    return await service.get_borrower(borrower_id)


@router.post("", response_model=BorrowerResponse, status_code=status.HTTP_201_CREATED)
async def create_borrower(
    payload: BorrowerCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BorrowerResponse:
    service = BorrowerService(BorrowerRepository(session))
    return await service.create_borrower(payload)


@router.patch("/{borrower_id}", response_model=BorrowerResponse)
async def update_borrower(
    borrower_id: UUID,
    payload: BorrowerUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BorrowerResponse:
    service = BorrowerService(BorrowerRepository(session))
    return await service.update_borrower(borrower_id, payload)


@router.delete("/{borrower_id}", response_model=BorrowerResponse)
async def archive_borrower(
    borrower_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BorrowerResponse:
    service = BorrowerService(BorrowerRepository(session))
    return await service.archive_borrower(borrower_id)
