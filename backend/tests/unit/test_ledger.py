from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.exceptions import ConflictError
from app.models.ledger import LedgerDirection, LedgerEntry, LedgerEntryType
from app.modules.ledger.schemas import LedgerEntryCreate
from app.modules.ledger.service import LedgerEntryService


class FakeLedgerEntryRepository:
    def __init__(self) -> None:
        self.items: dict[str, LedgerEntry] = {}

    async def create(self, data: dict[str, object]) -> LedgerEntry:
        record = LedgerEntry(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.entry_number] = record
        return record

    async def get_by_entry_number(self, entry_number: str) -> LedgerEntry | None:
        return self.items.get(entry_number)

    async def get_by_id(self, entry_id: uuid.UUID) -> LedgerEntry | None:
        for record in self.items.values():
            if record.id == entry_id:
                return record
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[LedgerEntry]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[LedgerEntry]:
        return list(self.items.values())

    async def update(self, entry: LedgerEntry, data: dict[str, object]) -> LedgerEntry:
        for key, value in data.items():
            setattr(entry, key, value)
        entry.updated_at = datetime.now(UTC)
        self.items[entry.entry_number] = entry
        return entry


@pytest.mark.asyncio
async def test_create_ledger_entry_succeeds() -> None:
    service = LedgerEntryService(FakeLedgerEntryRepository())
    organization_id = uuid.uuid4()

    record = await service.create_ledger_entry(
        LedgerEntryCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            entry_number="LED-1001",
            entry_type=LedgerEntryType.DISBURSEMENT,
            direction=LedgerDirection.DEBIT,
            amount=Decimal("1250.50"),
            balance_after=Decimal("1250.50"),
            notes="Initial disbursement",
        )
    )

    assert record.entry_number == "LED-1001"
    assert record.amount == Decimal("1250.50")
    assert record.direction == LedgerDirection.DEBIT.value


@pytest.mark.asyncio
async def test_create_ledger_entry_rejects_duplicate_number() -> None:
    repository = FakeLedgerEntryRepository()
    service = LedgerEntryService(repository)
    organization_id = uuid.uuid4()

    await service.create_ledger_entry(
        LedgerEntryCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            entry_number="LED-1002",
            amount=Decimal("500.00"),
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_ledger_entry(
            LedgerEntryCreate(
                organization_id=organization_id,
                loan_id=uuid.uuid4(),
                borrower_id=uuid.uuid4(),
                entry_number="LED-1002",
                amount=Decimal("300.00"),
            )
        )


@pytest.mark.asyncio
async def test_reverse_ledger_entry_creates_reversal_record() -> None:
    repository = FakeLedgerEntryRepository()
    service = LedgerEntryService(repository)
    organization_id = uuid.uuid4()

    original = await service.create_ledger_entry(
        LedgerEntryCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            entry_number="LED-1003",
            amount=Decimal("800.00"),
            direction=LedgerDirection.DEBIT,
        )
    )

    reversal = await service.reverse_ledger_entry(original.id)

    assert reversal.reversal_of_id == original.id
    assert reversal.entry_type == LedgerEntryType.REVERSAL.value
    assert reversal.direction == LedgerDirection.CREDIT.value
    assert reversal.amount == Decimal("800.00")


def test_create_ledger_entry_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError, match="greater than 0"):
        LedgerEntryCreate(
            organization_id=uuid.uuid4(),
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            entry_number="LED-1004",
            amount=Decimal("0.00"),
        )
