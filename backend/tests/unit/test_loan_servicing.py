from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.loan_servicing import LoanServicing, LoanServicingStatus
from app.modules.loan_servicing.schemas import LoanServicingCreate, LoanServicingUpdate
from app.modules.loan_servicing.service import LoanServicingService


class FakeLoanServicingRepository:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, LoanServicing] = {}

    async def create(self, data: dict[str, object]) -> LoanServicing:
        record = LoanServicing(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.id] = record
        return record

    async def get_by_id(self, servicing_id: uuid.UUID) -> LoanServicing | None:
        return self.items.get(servicing_id)

    async def get_by_loan_id(self, loan_id: uuid.UUID) -> LoanServicing | None:
        for record in self.items.values():
            if record.loan_id == loan_id:
                return record
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[LoanServicing]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[LoanServicing]:
        return list(self.items.values())

    async def update(self, record: LoanServicing, data: dict[str, object]) -> LoanServicing:
        for key, value in data.items():
            setattr(record, key, value)
        record.updated_at = datetime.now(UTC)
        return record


@pytest.mark.asyncio
async def test_create_servicing_record_succeeds() -> None:
    service = LoanServicingService(FakeLoanServicingRepository())
    organization_id = uuid.uuid4()
    loan_id = uuid.uuid4()

    record = await service.create_servicing_record(
        LoanServicingCreate(
            organization_id=organization_id,
            loan_id=loan_id,
            principal_outstanding=Decimal("5000.00"),
            interest_outstanding=Decimal("250.00"),
            total_outstanding=Decimal("5250.00"),
            next_due_date=datetime.now(UTC),
        )
    )

    assert record.loan_id == loan_id
    assert record.status == LoanServicingStatus.ACTIVE.value
    assert record.total_outstanding == Decimal("5250.00")


@pytest.mark.asyncio
async def test_create_servicing_record_rejects_duplicate_loan() -> None:
    repository = FakeLoanServicingRepository()
    service = LoanServicingService(repository)
    loan_id = uuid.uuid4()

    await service.create_servicing_record(
        LoanServicingCreate(
            organization_id=uuid.uuid4(),
            loan_id=loan_id,
            principal_outstanding=Decimal("200.00"),
            interest_outstanding=Decimal("10.00"),
            total_outstanding=Decimal("210.00"),
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_servicing_record(
            LoanServicingCreate(
                organization_id=uuid.uuid4(),
                loan_id=loan_id,
                principal_outstanding=Decimal("300.00"),
                interest_outstanding=Decimal("15.00"),
                total_outstanding=Decimal("315.00"),
            )
        )


@pytest.mark.asyncio
async def test_record_payment_reduces_balance() -> None:
    repository = FakeLoanServicingRepository()
    service = LoanServicingService(repository)
    loan_id = uuid.uuid4()

    record = await service.create_servicing_record(
        LoanServicingCreate(
            organization_id=uuid.uuid4(),
            loan_id=loan_id,
            principal_outstanding=Decimal("500.00"),
            interest_outstanding=Decimal("50.00"),
            total_outstanding=Decimal("550.00"),
            days_past_due=2,
        )
    )

    updated = await service.record_payment(loan_id, Decimal("200.00"))

    assert updated.last_payment_amount == Decimal("200.00")
    assert updated.total_outstanding == Decimal("350.00")
    assert updated.days_past_due == 1


@pytest.mark.asyncio
async def test_get_by_loan_id_raises_for_missing_record() -> None:
    service = LoanServicingService(FakeLoanServicingRepository())

    with pytest.raises(NotFoundError, match="not found"):
        await service.get_by_loan_id(uuid.uuid4())
