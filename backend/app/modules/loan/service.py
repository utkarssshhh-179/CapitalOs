from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.loan import Loan, LoanStatus
from app.modules.loan.repository import LoanRepository
from app.modules.loan.schemas import LoanCreate, LoanUpdate


class LoanService:
    def __init__(self, repository: LoanRepository) -> None:
        self.repository = repository

    async def create_loan(self, payload: LoanCreate) -> Loan:
        loan_number = payload.loan_number.strip()
        existing = await self.repository.get_by_loan_number(loan_number)
        if existing is not None:
            raise ConflictError("Loan with this number already exists", details={"loan_number": loan_number})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["loan_number"] = loan_number
        data.setdefault("status", LoanStatus.PENDING.value)
        return await self.repository.create(data)

    async def list_loans(self, organization_id: UUID | None = None) -> list[Loan]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_loan(self, loan_id: UUID) -> Loan:
        loan = await self.repository.get_by_id(loan_id)
        if loan is None:
            raise NotFoundError("Loan not found", details={"id": str(loan_id)})
        return loan

    async def update_loan(self, loan_id: UUID, payload: LoanUpdate) -> Loan:
        loan = await self.get_loan(loan_id)
        data = payload.model_dump(exclude_unset=True)

        if "loan_number" in data and data["loan_number"] is not None:
            value = str(data["loan_number"]).strip()
            if value != loan.loan_number and await self.repository.get_by_loan_number(value):
                raise ConflictError("Loan with this number already exists", details={"loan_number": value})
            data["loan_number"] = value

        if "status" in data and data["status"] is not None:
            data["status"] = LoanStatus(data["status"]).value

        return await self.repository.update(loan, data)

    async def mark_loan_closed(self, loan_id: UUID) -> Loan:
        loan = await self.get_loan(loan_id)
        return await self.repository.update(loan, {"status": LoanStatus.CLOSED.value})
