from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection


class CollectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Collection:
        record = Collection(**data)
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_by_id(self, collection_id: UUID) -> Collection | None:
        result = await self.session.execute(select(Collection).where(Collection.id == collection_id))
        return result.scalar_one_or_none()

    async def get_by_case_number(self, case_number: str) -> Collection | None:
        result = await self.session.execute(select(Collection).where(Collection.case_number == case_number))
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID) -> list[Collection]:
        result = await self.session.execute(
            select(Collection).where(Collection.organization_id == organization_id).order_by(Collection.created_at.desc())
        )
        return list(result.scalars().all())

    async def list(self) -> list[Collection]:
        result = await self.session.execute(select(Collection).order_by(Collection.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, collection: Collection, data: dict[str, Any]) -> Collection:
        for field, value in data.items():
            setattr(collection, field, value)
        await self.session.flush()
        return collection
