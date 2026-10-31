from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.loan import Loan, LoanStatus
from app.modules.loan.schemas import LoanCreate, LoanUpdate
from app.modules.loan.service import LoanService


class FakeLoanRepository:
    def __init__(self) -> None:
        self.items: dict[str, Loan] = {}

    async def create(self, data: dict[str, object]) -> Loan:
        loan = Loan(**data)
        loan.id = uuid.uuid4()
        loan.created_at = datetime.now(UTC)
        loan.updated_at = loan.created_at
        self.items[loan.loan_number] = loan
        return loan

    async def get_by_loan_number(self, loan_number: str) -> Loan | None:
        return self.items.get(loan_number)

    async def get_by_id(self, loan_id: uuid.UUID) -> Loan | None:
        for loan in self.items.values():
            if loan.id == loan_id:
                return loan
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Loan]:
        return [loan for loan in self.items.values() if loan.organization_id == organization_id]

    async def list(self) -> list[Loan]:
        return list(self.items.values())

    async def update(self, loan: Loan, data: dict[str, object]) -> Loan:
        for key, value in data.items():
            setattr(loan, key, value)
        loan.updated_at = datetime.now(UTC)
        self.items[loan.loan_number] = loan
        return loan


@pytest.mark.asyncio
async def test_create_loan_succeeds() -> None:
    service = LoanService(FakeLoanRepository())
    organization_id = uuid.uuid4()
    borrower_id = uuid.uuid4()
    investor_id = uuid.uuid4()

    loan = await service.create_loan(
        LoanCreate(
            organization_id=organization_id,
            borrower_id=borrower_id,
            investor_id=investor_id,
            loan_number="LN-1001",
            principal_amount=250000,
            interest_rate=12.5,
            tenure_months=24,
            purpose="Business expansion",
        )
    )

    assert loan.loan_number == "LN-1001"
    assert loan.organization_id == organization_id
    assert loan.status == LoanStatus.PENDING.value


@pytest.mark.asyncio
async def test_create_loan_rejects_duplicate_loan_number() -> None:
    repository = FakeLoanRepository()
    service = LoanService(repository)
    organization_id = uuid.uuid4()

    await service.create_loan(
        LoanCreate(
            organization_id=organization_id,
            borrower_id=uuid.uuid4(),
            investor_id=uuid.uuid4(),
            loan_number="LN-1001",
            principal_amount=250000,
            interest_rate=12.5,
            tenure_months=24,
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_loan(
            LoanCreate(
                organization_id=organization_id,
                borrower_id=uuid.uuid4(),
                investor_id=uuid.uuid4(),
                loan_number="LN-1001",
                principal_amount=370000,
                interest_rate=11.0,
                tenure_months=18,
            )
        )


@pytest.mark.asyncio
async def test_update_loan_changes_status() -> None:
    repository = FakeLoanRepository()
    service = LoanService(repository)
    organization_id = uuid.uuid4()

    loan = await service.create_loan(
        LoanCreate(
            organization_id=organization_id,
            borrower_id=uuid.uuid4(),
            investor_id=uuid.uuid4(),
            loan_number="LN-1002",
            principal_amount=300000,
            interest_rate=13.0,
            tenure_months=12,
        )
    )

    updated = await service.update_loan(loan.id, LoanUpdate(status=LoanStatus.APPROVED))

    assert updated.status == LoanStatus.APPROVED.value
