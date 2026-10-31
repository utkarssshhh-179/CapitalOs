from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.loan_schedule import LoanSchedule


class LoanScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> LoanSchedule:
        record = LoanSchedule(**data)
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_by_id(self, schedule_id: UUID) -> LoanSchedule | None:
        result = await self.session.execute(select(LoanSchedule).where(LoanSchedule.id == schedule_id))
        return result.scalar_one_or_none()

    async def list_by_loan(self, loan_id: UUID) -> list[LoanSchedule]:
        result = await self.session.execute(
            select(LoanSchedule).where(LoanSchedule.loan_id == loan_id).order_by(LoanSchedule.installment_number.asc())
        )
        return list(result.scalars().all())

    async def list_by_organization(self, organization_id: UUID) -> list[LoanSchedule]:
        result = await self.session.execute(
            select(LoanSchedule).where(LoanSchedule.organization_id == organization_id).order_by(LoanSchedule.due_date.asc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[LoanSchedule]:
        result = await self.session.execute(select(LoanSchedule).order_by(LoanSchedule.due_date.asc()))
        return list(result.scalars().all())

    async def update(self, record: LoanSchedule, data: dict[str, Any]) -> LoanSchedule:
        for field, value in data.items():
            setattr(record, field, value)
        await self.session.flush()
        return record
