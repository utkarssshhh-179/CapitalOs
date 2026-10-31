from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.loan import Loan


class LoanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Loan:
        loan = Loan(**data)
        self.session.add(loan)
        await self.session.flush()
        return loan

    async def get_by_id(self, loan_id: UUID) -> Loan | None:
        result = await self.session.execute(select(Loan).where(Loan.id == loan_id))
        return result.scalar_one_or_none()

    async def get_by_loan_number(self, loan_number: str) -> Loan | None:
        result = await self.session.execute(select(Loan).where(Loan.loan_number == loan_number))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[Loan]:
        result = await self.session.execute(
            select(Loan).where(Loan.organization_id == organization_id).order_by(Loan.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[Loan]:
        result = await self.session.execute(select(Loan).order_by(Loan.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, loan: Loan, data: dict[str, Any]) -> Loan:
        for field, value in data.items():
            setattr(loan, field, value)
        await self.session.flush()
        return loan
