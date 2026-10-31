from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.collection import Collection, CollectionStatus
from app.modules.collection.schemas import CollectionCreate, CollectionUpdate
from app.modules.collection.service import CollectionService


class FakeCollectionRepository:
    def __init__(self) -> None:
        self.items: dict[str, Collection] = {}

    async def create(self, data: dict[str, object]) -> Collection:
        record = Collection(**data)
        record.id = uuid.uuid4()
        record.created_at = datetime.now(UTC)
        record.updated_at = record.created_at
        self.items[record.case_number] = record
        return record

    async def get_by_case_number(self, case_number: str) -> Collection | None:
        return self.items.get(case_number)

    async def get_by_id(self, collection_id: uuid.UUID) -> Collection | None:
        for record in self.items.values():
            if record.id == collection_id:
                return record
        return None

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Collection]:
        return [record for record in self.items.values() if record.organization_id == organization_id]

    async def list(self) -> list[Collection]:
        return list(self.items.values())

    async def update(self, collection: Collection, data: dict[str, object]) -> Collection:
        for key, value in data.items():
            setattr(collection, key, value)
        collection.updated_at = datetime.now(UTC)
        self.items[collection.case_number] = collection
        return collection


@pytest.mark.asyncio
async def test_create_collection_succeeds() -> None:
    service = CollectionService(FakeCollectionRepository())
    organization_id = uuid.uuid4()

    record = await service.create_collection(
        CollectionCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            case_number="CASE-1001",
            assigned_to="Ravi",
        )
    )

    assert record.case_number == "CASE-1001"
    assert record.organization_id == organization_id
    assert record.status == CollectionStatus.OPEN.value


@pytest.mark.asyncio
async def test_create_collection_rejects_duplicate_case_number() -> None:
    repository = FakeCollectionRepository()
    service = CollectionService(repository)
    organization_id = uuid.uuid4()

    await service.create_collection(
        CollectionCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            case_number="CASE-1001",
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_collection(
            CollectionCreate(
                organization_id=organization_id,
                loan_id=uuid.uuid4(),
                borrower_id=uuid.uuid4(),
                case_number="CASE-1001",
            )
        )


@pytest.mark.asyncio
async def test_update_collection_changes_status() -> None:
    repository = FakeCollectionRepository()
    service = CollectionService(repository)
    organization_id = uuid.uuid4()

    record = await service.create_collection(
        CollectionCreate(
            organization_id=organization_id,
            loan_id=uuid.uuid4(),
            borrower_id=uuid.uuid4(),
            case_number="CASE-1002",
        )
    )

    updated = await service.update_collection(record.id, CollectionUpdate(status=CollectionStatus.CONTACTED))

    assert updated.status == CollectionStatus.CONTACTED.value
