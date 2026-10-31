from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.collection import Collection, CollectionStatus
from app.modules.collection.repository import CollectionRepository
from app.modules.collection.schemas import CollectionCreate, CollectionUpdate


class CollectionService:
    def __init__(self, repository: CollectionRepository) -> None:
        self.repository = repository

    async def create_collection(self, payload: CollectionCreate) -> Collection:
        case_number = payload.case_number.strip()
        existing = await self.repository.get_by_case_number(case_number)
        if existing is not None:
            raise ConflictError("Collection case with this number already exists", details={"case_number": case_number})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["case_number"] = case_number
        data.setdefault("status", CollectionStatus.OPEN.value)
        return await self.repository.create(data)

    async def list_collections(self, organization_id: UUID | None = None) -> list[Collection]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_collection(self, collection_id: UUID) -> Collection:
        collection = await self.repository.get_by_id(collection_id)
        if collection is None:
            raise NotFoundError("Collection case not found", details={"id": str(collection_id)})
        return collection

    async def update_collection(self, collection_id: UUID, payload: CollectionUpdate) -> Collection:
        collection = await self.get_collection(collection_id)
        data = payload.model_dump(exclude_unset=True)

        if "case_number" in data and data["case_number"] is not None:
            value = str(data["case_number"]).strip()
            if value != collection.case_number and await self.repository.get_by_case_number(value):
                raise ConflictError("Collection case with this number already exists", details={"case_number": value})
            data["case_number"] = value

        if "status" in data and data["status"] is not None:
            data["status"] = CollectionStatus(data["status"]).value

        return await self.repository.update(collection, data)

    async def resolve_collection(self, collection_id: UUID) -> Collection:
        collection = await self.get_collection(collection_id)
        return await self.repository.update(collection, {"status": CollectionStatus.RESOLVED.value})
