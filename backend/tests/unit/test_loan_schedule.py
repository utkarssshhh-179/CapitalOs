from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.models.loan_schedule import LoanSchedule, LoanScheduleStatus
from app.modules.loan_schedule.schemas import LoanScheduleCreate
from app.modules.loan_schedule.service import LoanScheduleService


class FakeLoanScheduleRepository:
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, LoanSchedule] = {}

    async def create(self, data: dict[str, object]) -> LoanSchedule:
        record = LoanSchedule(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.id] = record
        return record

    async def get_by_id(self, schedule_id: uuid.UUID) -> LoanSchedule | None:
        return self.items.get(schedule_id)

    async def list_by_loan(self, loan_id: uuid.UUID) -> list[LoanSchedule]:
        return [record for record in self.items.values() if record.loan_id == loan_id]

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[LoanSchedule]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[LoanSchedule]:
        return list(self.items.values())

    async def update(self, record: LoanSchedule, data: dict[str, object]) -> LoanSchedule:
        for key, value in data.items():
            setattr(record, key, value)
        record.updated_at = datetime.now(UTC)
        return record


@pytest.mark.asyncio
async def test_create_schedule_entry_succeeds() -> None:
    service = LoanScheduleService(FakeLoanScheduleRepository())
    organization_id = uuid.uuid4()
    loan_id = uuid.uuid4()

    schedule = await service.create_schedule_entry(
        LoanScheduleCreate(
            organization_id=organization_id,
            loan_id=loan_id,
            installment_number=1,
            due_date=datetime.now(UTC),
            principal_component=Decimal("1000.00"),
            interest_component=Decimal("50.00"),
            total_installment=Decimal("1050.00"),
        )
    )

    assert schedule.installment_number == 1
    assert schedule.total_installment == Decimal("1050.00")
    assert schedule.status == LoanScheduleStatus.SCHEDULED.value


@pytest.mark.asyncio
async def test_generate_schedule_produces_expected_length() -> None:
    service = LoanScheduleService(FakeLoanScheduleRepository())
    organization_id = uuid.uuid4()
    loan_id = uuid.uuid4()

    schedule_entries = service.generate_schedule(
        organization_id=organization_id,
        loan_id=loan_id,
        principal_amount="12000",
        annual_interest_rate="12",
        tenure_months=12,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert len(schedule_entries) == 12
    assert schedule_entries[0].installment_number == 1
    assert schedule_entries[0].total_installment > Decimal("0")
    assert schedule_entries[-1].total_installment > Decimal("0")


@pytest.mark.asyncio
async def test_generate_schedule_has_positive_totals() -> None:
    service = LoanScheduleService(FakeLoanScheduleRepository())

    schedules = service.generate_schedule(
        organization_id=uuid.uuid4(),
        loan_id=uuid.uuid4(),
        principal_amount=Decimal("5000"),
        annual_interest_rate=Decimal("10"),
        tenure_months=6,
    )

    assert sum(item.total_installment for item in schedules) > Decimal("5000")
    assert all(item.total_installment > Decimal("0") for item in schedules)
