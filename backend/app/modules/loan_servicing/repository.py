from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.loan_servicing import LoanServicing


class LoanServicingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> LoanServicing:
        record = LoanServicing(**data)
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_by_id(self, servicing_id: UUID) -> LoanServicing | None:
        result = await self.session.execute(select(LoanServicing).where(LoanServicing.id == servicing_id))
        return result.scalar_one_or_none()

    async def get_by_loan_id(self, loan_id: UUID) -> LoanServicing | None:
        result = await self.session.execute(select(LoanServicing).where(LoanServicing.loan_id == loan_id))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[LoanServicing]:
        result = await self.session.execute(
            select(LoanServicing).where(LoanServicing.organization_id == organization_id).order_by(LoanServicing.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[LoanServicing]:
        result = await self.session.execute(select(LoanServicing).order_by(LoanServicing.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, record: LoanServicing, data: dict[str, Any]) -> LoanServicing:
        for field, value in data.items():
            setattr(record, field, value)
        await self.session.flush()
        return record
