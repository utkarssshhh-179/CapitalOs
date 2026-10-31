from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.money import ZERO, to_money
from app.models.ledger import LedgerDirection, LedgerEntry, LedgerEntryType
from app.modules.ledger.repository import LedgerEntryRepository
from app.modules.ledger.schemas import LedgerEntryCreate, LedgerEntryUpdate


class LedgerEntryService:
    def __init__(self, repository: LedgerEntryRepository) -> None:
        self.repository = repository

    async def create_ledger_entry(self, payload: LedgerEntryCreate) -> LedgerEntry:
        entry_number = payload.entry_number.strip()
        existing = await self.repository.get_by_entry_number(entry_number)
        if existing is not None:
            raise ConflictError("Ledger entry with this number already exists", details={"entry_number": entry_number})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["entry_number"] = entry_number
        data["amount"] = to_money(data["amount"])

        if data.get("balance_after") is not None:
            data["balance_after"] = to_money(data["balance_after"])

        data.setdefault("entry_type", LedgerEntryType.PAYMENT.value)
        data.setdefault("direction", LedgerDirection.DEBIT.value)

        if data["amount"] <= ZERO:
            raise BusinessRuleError("Ledger entry amount must be greater than zero")

        return await self.repository.create(data)

    async def list_ledger_entries(self, organization_id: UUID | None = None) -> list[LedgerEntry]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_ledger_entry(self, entry_id: UUID) -> LedgerEntry:
        entry = await self.repository.get_by_id(entry_id)
        if entry is None:
            raise NotFoundError("Ledger entry not found", details={"id": str(entry_id)})
        return entry

    async def update_ledger_entry(self, entry_id: UUID, payload: LedgerEntryUpdate) -> LedgerEntry:
        entry = await self.get_ledger_entry(entry_id)
        data = payload.model_dump(exclude_unset=True)

        if "entry_number" in data and data["entry_number"] is not None:
            value = str(data["entry_number"]).strip()
            if value != entry.entry_number and await self.repository.get_by_entry_number(value):
                raise ConflictError("Ledger entry with this number already exists", details={"entry_number": value})
            data["entry_number"] = value

        if "amount" in data and data["amount"] is not None:
            value = to_money(data["amount"])
            if value <= ZERO:
                raise BusinessRuleError("Ledger entry amount must be greater than zero")
            data["amount"] = value

        if "balance_after" in data and data["balance_after"] is not None:
            data["balance_after"] = to_money(data["balance_after"])

        if "entry_type" in data and data["entry_type"] is not None:
            data["entry_type"] = LedgerEntryType(data["entry_type"]).value

        if "direction" in data and data["direction"] is not None:
            data["direction"] = LedgerDirection(data["direction"]).value

        return await self.repository.update(entry, data)

    async def reverse_ledger_entry(self, entry_id: UUID, notes: str | None = None) -> LedgerEntry:
        entry = await self.get_ledger_entry(entry_id)
        if entry.reversal_of_id is not None:
            raise BusinessRuleError("This ledger entry is already a reversal")

        reversal_number = f"REV-{entry.entry_number}"
        if await self.repository.get_by_entry_number(reversal_number):
            raise ConflictError("Reversal ledger entry already exists", details={"entry_number": reversal_number})

        direction = (
            LedgerDirection.CREDIT.value
            if entry.direction == LedgerDirection.DEBIT.value
            else LedgerDirection.DEBIT.value
        )

        return await self.repository.create(
            {
                "organization_id": entry.organization_id,
                "loan_id": entry.loan_id,
                "borrower_id": entry.borrower_id,
                "entry_number": reversal_number,
                "entry_type": LedgerEntryType.REVERSAL.value,
                "direction": direction,
                "amount": entry.amount,
                "balance_after": None,
                "reversal_of_id": entry.id,
                "related_payment_id": entry.related_payment_id,
                "related_collection_id": entry.related_collection_id,
                "effective_at": entry.effective_at,
                "notes": notes or f"Reversal of {entry.entry_number}",
            }
        )
