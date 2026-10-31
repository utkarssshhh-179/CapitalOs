from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.borrower import Borrower, BorrowerStatus
from app.modules.borrower.schemas import BorrowerCreate, BorrowerUpdate
from app.modules.borrower.service import BorrowerService


class FakeBorrowerRepository:
    def __init__(self) -> None:
        self.items: dict[tuple[uuid.UUID, str], Borrower] = {}

    async def create(self, data: dict[str, object]) -> Borrower:
        borrower = Borrower(**data)
        borrower.id = uuid.uuid4()
        borrower.created_at = datetime.now(UTC)
        borrower.updated_at = borrower.created_at
        self.items[(borrower.organization_id, borrower.email)] = borrower
        return borrower

    async def get_by_email_and_organization(self, organization_id: uuid.UUID, email: str) -> Borrower | None:
        return self.items.get((organization_id, email.lower()))

    async def get_by_id(self, borrower_id: uuid.UUID) -> Borrower | None:
        for borrower in self.items.values():
            if borrower.id == borrower_id:
                return borrower
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Borrower]:
        return [borrower for (borrower_organization_id, _), borrower in self.items.items() if borrower_organization_id == organization_id]

    async def list(self) -> list[Borrower]:
        return list(self.items.values())

    async def update(self, borrower: Borrower, data: dict[str, object]) -> Borrower:
        for key, value in data.items():
            setattr(borrower, key, value)
        borrower.updated_at = datetime.now(UTC)
        self.items[(borrower.organization_id, borrower.email)] = borrower
        return borrower


@pytest.mark.asyncio
async def test_create_borrower_succeeds() -> None:
    service = BorrowerService(FakeBorrowerRepository())
    organization_id = uuid.uuid4()

    borrower = await service.create_borrower(
        BorrowerCreate(
            organization_id=organization_id,
            first_name="Jane",
            last_name="Doe",
            email="jane@capitalos.io",
            phone="+91-9876543210",
        )
    )

    assert borrower.first_name == "Jane"
    assert borrower.organization_id == organization_id
    assert borrower.status == BorrowerStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_create_borrower_rejects_duplicate_email_in_same_org() -> None:
    repository = FakeBorrowerRepository()
    service = BorrowerService(repository)
    organization_id = uuid.uuid4()

    await service.create_borrower(
        BorrowerCreate(
            organization_id=organization_id,
            first_name="Jane",
            last_name="Doe",
            email="jane@capitalos.io",
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_borrower(
            BorrowerCreate(
                organization_id=organization_id,
                first_name="Jane",
                last_name="Smith",
                email="JANE@capitalos.io",
            )
        )


@pytest.mark.asyncio
async def test_update_borrower_changes_status() -> None:
    repository = FakeBorrowerRepository()
    service = BorrowerService(repository)
    organization_id = uuid.uuid4()

    borrower = await service.create_borrower(
        BorrowerCreate(
            organization_id=organization_id,
            first_name="Jane",
            last_name="Doe",
            email="jane@capitalos.io",
        )
    )

    updated = await service.update_borrower(
        borrower.id,
        BorrowerUpdate(status=BorrowerStatus.BLACKLISTED),
    )

    assert updated.status == BorrowerStatus.BLACKLISTED.value
