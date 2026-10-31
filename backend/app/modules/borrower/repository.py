from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrower import Borrower


class BorrowerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Borrower:
        borrower = Borrower(**data)
        self.session.add(borrower)
        await self.session.flush()
        return borrower

    async def get_by_id(self, borrower_id: UUID) -> Borrower | None:
        result = await self.session.execute(select(Borrower).where(Borrower.id == borrower_id))
        return result.scalar_one_or_none()

    async def get_by_email_and_organization(self, organization_id: UUID, email: str) -> Borrower | None:
        result = await self.session.execute(
            select(Borrower).where(Borrower.organization_id == organization_id, Borrower.email == email)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[Borrower]:
        result = await self.session.execute(
            select(Borrower).where(Borrower.organization_id == organization_id).order_by(Borrower.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[Borrower]:
        result = await self.session.execute(select(Borrower).order_by(Borrower.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, borrower: Borrower, data: dict[str, Any]) -> Borrower:
        for field, value in data.items():
            setattr(borrower, field, value)
        await self.session.flush()
        return borrower
