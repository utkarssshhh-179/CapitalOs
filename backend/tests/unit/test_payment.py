from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.payment import Payment, PaymentStatus
from app.modules.payment.schemas import PaymentCreate, PaymentUpdate
from app.modules.payment.service import PaymentService


class FakePaymentRepository:
    def __init__(self) -> None:
        self.items: dict[str, Payment] = {}

    async def create(self, data: dict[str, object]) -> Payment:
        payment = Payment(**data)
        payment.id = uuid.uuid4()
        payment.created_at = datetime.now(UTC)
        payment.updated_at = payment.created_at
        self.items[payment.payment_number] = payment
        return payment

    async def get_by_payment_number(self, payment_number: str) -> Payment | None:
        return self.items.get(payment_number)

    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        for payment in self.items.values():
            if payment.id == payment_id:
                return payment
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Payment]:
        return [payment for payment in self.items.values() if payment.organization_id == organization_id]

    async def list(self) -> list[Payment]:
        return list(self.items.values())

    async def update(self, payment: Payment, data: dict[str, object]) -> Payment:
        for key, value in data.items():
            setattr(payment, key, value)
        payment.updated_at = datetime.now(UTC)
        self.items[payment.payment_number] = payment
        return payment


@pytest.mark.asyncio
async def test_create_payment_succeeds() -> None:
    service = PaymentService(FakePaymentRepository())
    organization_id = uuid.uuid4()
    loan_id = uuid.uuid4()
    borrower_id = uuid.uuid4()

    payment = await service.create_payment(
        PaymentCreate(
            organization_id=organization_id,
            loan_id=loan_id,
            borrower_id=borrower_id,
            payment_number="PMT-1001",
            amount=50000,
            payment_mode="upi",
        )
    )

    assert payment.payment_number == "PMT-1001"
    assert payment.organization_id == organization_id
    assert payment.status == PaymentStatus.PENDING.value


@pytest.mark.asyncio
async def test_create_payment_rejects_duplicate_number() -> None:
    repository = FakePaymentRepository()
    service = PaymentService(repository)
    organization_id = uuid.uuid4()

    await service.create_payment(
        PaymentCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            payment_number="PMT-1001",
            amount=50000,
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_payment(
            PaymentCreate(
                organization_id=organization_id,
                loan_id=uuid.uuid4(),
                borrower_id=uuid.uuid4(),
                payment_number="PMT-1001",
                amount=75000,
            )
        )


@pytest.mark.asyncio
async def test_update_payment_changes_status() -> None:
    repository = FakePaymentRepository()
    service = PaymentService(repository)
    organization_id = uuid.uuid4()

    payment = await service.create_payment(
        PaymentCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            payment_number="PMT-1002",
            amount=65000,
        )
    )

    updated = await service.update_payment(payment.id, PaymentUpdate(status=PaymentStatus.PAID))

    assert updated.status == PaymentStatus.PAID.value
