from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import LedgerEntry


class LedgerEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> LedgerEntry:
        entry = LedgerEntry(**data)
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_by_id(self, entry_id: UUID) -> LedgerEntry | None:
        result = await self.session.execute(select(LedgerEntry).where(LedgerEntry.id == entry_id))
        return result.scalar_one_or_none()

    async def get_by_entry_number(self, entry_number: str) -> LedgerEntry | None:
        result = await self.session.execute(select(LedgerEntry).where(LedgerEntry.entry_number == entry_number))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[LedgerEntry]:
        result = await self.session.execute(
            select(LedgerEntry).where(LedgerEntry.organization_id == organization_id).order_by(LedgerEntry.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[LedgerEntry]:
        result = await self.session.execute(select(LedgerEntry).order_by(LedgerEntry.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, entry: LedgerEntry, data: dict[str, Any]) -> LedgerEntry:
        for field, value in data.items():
            setattr(entry, field, value)
        await self.session.flush()
        return entry
