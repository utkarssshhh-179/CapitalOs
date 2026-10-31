from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.investor import Investor, InvestorStatus
from app.modules.investor.schemas import InvestorCreate, InvestorUpdate
from app.modules.investor.service import InvestorService


class FakeInvestorRepository:
    def __init__(self) -> None:
        self.items: dict[tuple[uuid.UUID, str], Investor] = {}

    async def create(self, data: dict[str, object]) -> Investor:
        investor = Investor(**data)
        investor.id = uuid.uuid4()
        investor.created_at = datetime.now(UTC)
        investor.updated_at = investor.created_at
        self.items[(investor.organization_id, investor.email)] = investor
        return investor

    async def get_by_email_and_organization(self, organization_id: uuid.UUID, email: str) -> Investor | None:
        return self.items.get((organization_id, email.lower()))

    async def get_by_id(self, investor_id: uuid.UUID) -> Investor | None:
        for investor in self.items.values():
            if investor.id == investor_id:
                return investor
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Investor]:
        return [investor for (investor_organization_id, _), investor in self.items.items() if investor_organization_id == organization_id]

    async def list(self) -> list[Investor]:
        return list(self.items.values())

    async def update(self, investor: Investor, data: dict[str, object]) -> Investor:
        for key, value in data.items():
            setattr(investor, key, value)
        investor.updated_at = datetime.now(UTC)
        self.items[(investor.organization_id, investor.email)] = investor
        return investor


@pytest.mark.asyncio
async def test_create_investor_succeeds() -> None:
    service = InvestorService(FakeInvestorRepository())
    organization_id = uuid.uuid4()

    investor = await service.create_investor(
        InvestorCreate(
            organization_id=organization_id,
            first_name="Alice",
            last_name="Ng",
            email="alice@capitalos.io",
            company_name="Northwind Capital",
        )
    )

    assert investor.first_name == "Alice"
    assert investor.organization_id == organization_id
    assert investor.status == InvestorStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_create_investor_rejects_duplicate_email_in_same_org() -> None:
    repository = FakeInvestorRepository()
    service = InvestorService(repository)
    organization_id = uuid.uuid4()

    await service.create_investor(
        InvestorCreate(
            organization_id=organization_id,
            first_name="Alice",
            last_name="Ng",
            email="alice@capitalos.io",
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_investor(
            InvestorCreate(
                organization_id=organization_id,
                first_name="Alicia",
                last_name="Ng",
                email="ALICE@capitalos.io",
            )
        )


@pytest.mark.asyncio
async def test_update_investor_changes_status() -> None:
    repository = FakeInvestorRepository()
    service = InvestorService(repository)
    organization_id = uuid.uuid4()

    investor = await service.create_investor(
        InvestorCreate(
            organization_id=organization_id,
            first_name="Alice",
            last_name="Ng",
            email="alice@capitalos.io",
        )
    )

    updated = await service.update_investor(
        investor.id,
        InvestorUpdate(status=InvestorStatus.RESTRICTED),
    )

    assert updated.status == InvestorStatus.RESTRICTED.value
