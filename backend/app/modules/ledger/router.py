from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.ledger.repository import LedgerEntryRepository
from app.modules.ledger.schemas import LedgerEntryCreate, LedgerEntryResponse, LedgerEntryUpdate
from app.modules.ledger.service import LedgerEntryService

router = APIRouter(prefix="/ledger-entries", tags=["ledger"])


@router.get("", response_model=list[LedgerEntryResponse])
async def list_ledger_entries(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[LedgerEntryResponse]:
    service = LedgerEntryService(LedgerEntryRepository(session))
    return await service.list_ledger_entries(organization_id)


@router.get("/{entry_id}", response_model=LedgerEntryResponse)
async def get_ledger_entry(
    entry_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LedgerEntryResponse:
    service = LedgerEntryService(LedgerEntryRepository(session))
    return await service.get_ledger_entry(entry_id)


@router.post("", response_model=LedgerEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_ledger_entry(
    payload: LedgerEntryCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LedgerEntryResponse:
    service = LedgerEntryService(LedgerEntryRepository(session))
    return await service.create_ledger_entry(payload)


@router.patch("/{entry_id}", response_model=LedgerEntryResponse)
async def update_ledger_entry(
    entry_id: UUID,
    payload: LedgerEntryUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LedgerEntryResponse:
    service = LedgerEntryService(LedgerEntryRepository(session))
    return await service.update_ledger_entry(entry_id, payload)


@router.post("/{entry_id}/reverse", response_model=LedgerEntryResponse, status_code=status.HTTP_201_CREATED)
async def reverse_ledger_entry(
    entry_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    notes: str | None = None,
) -> LedgerEntryResponse:
    service = LedgerEntryService(LedgerEntryRepository(session))
    return await service.reverse_ledger_entry(entry_id, notes)
