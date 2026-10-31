from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Organization:
        organization = Organization(**data)
        self.session.add(organization)
        await self.session.flush()
        return organization

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(Organization.email == email)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Organization]:
        result = await self.session.execute(
            select(Organization).order_by(Organization.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, organization: Organization, data: dict[str, Any]) -> Organization:
        for field, value in data.items():
            setattr(organization, field, value)
        await self.session.flush()
        return organization
