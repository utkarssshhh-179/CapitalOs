from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Payment:
        payment = Payment(**data)
        self.session.add(payment)
        await self.session.flush()
        return payment

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def get_by_payment_number(self, payment_number: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.payment_number == payment_number))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.organization_id == organization_id).order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[Payment]:
        result = await self.session.execute(select(Payment).order_by(Payment.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, payment: Payment, data: dict[str, Any]) -> Payment:
        for field, value in data.items():
            setattr(payment, field, value)
        await self.session.flush()
        return payment
