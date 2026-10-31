from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investor import Investor


class InvestorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Investor:
        investor = Investor(**data)
        self.session.add(investor)
        await self.session.flush()
        return investor

    async def get_by_id(self, investor_id: UUID) -> Investor | None:
        result = await self.session.execute(select(Investor).where(Investor.id == investor_id))
        return result.scalar_one_or_none()

    async def get_by_email_and_organization(self, organization_id: UUID, email: str) -> Investor | None:
        result = await self.session.execute(
            select(Investor).where(Investor.organization_id == organization_id, Investor.email == email)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[Investor]:
        result = await self.session.execute(
            select(Investor).where(Investor.organization_id == organization_id).order_by(Investor.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[Investor]:
        result = await self.session.execute(select(Investor).order_by(Investor.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, investor: Investor, data: dict[str, Any]) -> Investor:
        for field, value in data.items():
            setattr(investor, field, value)
        await self.session.flush()
        return investor
