from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.payment import Payment, PaymentStatus
from app.modules.payment.repository import PaymentRepository
from app.modules.payment.schemas import PaymentCreate, PaymentUpdate


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    async def create_payment(self, payload: PaymentCreate) -> Payment:
        payment_number = payload.payment_number.strip()
        existing = await self.repository.get_by_payment_number(payment_number)
        if existing is not None:
            raise ConflictError("Payment with this number already exists", details={"payment_number": payment_number})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["payment_number"] = payment_number
        data.setdefault("status", PaymentStatus.PENDING.value)
        return await self.repository.create(data)

    async def list_payments(self, organization_id: UUID | None = None) -> list[Payment]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_payment(self, payment_id: UUID) -> Payment:
        payment = await self.repository.get_by_id(payment_id)
        if payment is None:
            raise NotFoundError("Payment not found", details={"id": str(payment_id)})
        return payment

    async def update_payment(self, payment_id: UUID, payload: PaymentUpdate) -> Payment:
        payment = await self.get_payment(payment_id)
        data = payload.model_dump(exclude_unset=True)

        if "payment_number" in data and data["payment_number"] is not None:
            value = str(data["payment_number"]).strip()
            if value != payment.payment_number and await self.repository.get_by_payment_number(value):
                raise ConflictError("Payment with this number already exists", details={"payment_number": value})
            data["payment_number"] = value

        if "status" in data and data["status"] is not None:
            data["status"] = PaymentStatus(data["status"]).value

        return await self.repository.update(payment, data)

    async def mark_payment_paid(self, payment_id: UUID) -> Payment:
        payment = await self.get_payment(payment_id)
        return await self.repository.update(payment, {"status": PaymentStatus.PAID.value})
