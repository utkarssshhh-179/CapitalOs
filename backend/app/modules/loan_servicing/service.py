from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.core.money import ZERO, to_money
from app.models.loan_servicing import LoanServicing, LoanServicingStatus
from app.modules.loan_servicing.repository import LoanServicingRepository
from app.modules.loan_servicing.schemas import LoanServicingCreate, LoanServicingUpdate


class LoanServicingService:
    def __init__(self, repository: LoanServicingRepository) -> None:
        self.repository = repository

    async def create_servicing_record(self, payload: LoanServicingCreate) -> LoanServicing:
        existing = await self.repository.get_by_loan_id(payload.loan_id)
        if existing is not None:
            raise ConflictError("Servicing record already exists for this loan", details={"loan_id": str(payload.loan_id)})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["principal_outstanding"] = to_money(data["principal_outstanding"])
        data["interest_outstanding"] = to_money(data["interest_outstanding"])
        data["total_outstanding"] = to_money(data["total_outstanding"])
        if data.get("last_payment_amount") is not None:
            data["last_payment_amount"] = to_money(data["last_payment_amount"])
        data.setdefault("status", LoanServicingStatus.ACTIVE.value)
        data.setdefault("days_past_due", 0)
        return await self.repository.create(data)

    async def list_servicing_records(self, organization_id: UUID | None = None) -> list[LoanServicing]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_servicing_record(self, servicing_id: UUID) -> LoanServicing:
        record = await self.repository.get_by_id(servicing_id)
        if record is None:
            raise NotFoundError("Loan servicing record not found", details={"id": str(servicing_id)})
        return record

    async def get_by_loan_id(self, loan_id: UUID) -> LoanServicing:
        record = await self.repository.get_by_loan_id(loan_id)
        if record is None:
            raise NotFoundError("Loan servicing record not found", details={"loan_id": str(loan_id)})
        return record

    async def update_servicing_record(self, servicing_id: UUID, payload: LoanServicingUpdate) -> LoanServicing:
        record = await self.get_servicing_record(servicing_id)
        data = payload.model_dump(exclude_unset=True)

        if "principal_outstanding" in data and data["principal_outstanding"] is not None:
            data["principal_outstanding"] = to_money(data["principal_outstanding"])
        if "interest_outstanding" in data and data["interest_outstanding"] is not None:
            data["interest_outstanding"] = to_money(data["interest_outstanding"])
        if "total_outstanding" in data and data["total_outstanding"] is not None:
            data["total_outstanding"] = to_money(data["total_outstanding"])
        if "last_payment_amount" in data and data["last_payment_amount"] is not None:
            data["last_payment_amount"] = to_money(data["last_payment_amount"])
        if "status" in data and data["status"] is not None:
            data["status"] = LoanServicingStatus(data["status"]).value

        return await self.repository.update(record, data)

    async def record_payment(self, loan_id: UUID, payment_amount: Decimal | int | str, payment_date: datetime | None = None) -> LoanServicing:
        record = await self.get_by_loan_id(loan_id)
        amount = to_money(payment_amount)
        if amount <= ZERO:
            raise ValueError("payment_amount must be greater than zero")

        record.last_payment_amount = amount
        record.last_payment_date = payment_date or datetime.now()
        record.total_outstanding = to_money(record.total_outstanding - amount)
        record.principal_outstanding = to_money(max(record.principal_outstanding - amount, Decimal("0.00")))
        record.days_past_due = max(record.days_past_due - 1, 0)

        if record.total_outstanding <= ZERO:
            record.status = LoanServicingStatus.CURRENT.value
            record.total_outstanding = Decimal("0.00")
            record.principal_outstanding = Decimal("0.00")
            record.interest_outstanding = Decimal("0.00")

        return await self.repository.update(record, {
            "status": record.status,
            "principal_outstanding": record.principal_outstanding,
            "interest_outstanding": record.interest_outstanding,
            "total_outstanding": record.total_outstanding,
            "last_payment_amount": record.last_payment_amount,
            "last_payment_date": record.last_payment_date,
            "days_past_due": record.days_past_due,
        })
