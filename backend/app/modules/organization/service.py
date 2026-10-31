from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.organization import Organization, OrganizationStatus
from app.modules.organization.repository import OrganizationRepository
from app.modules.organization.schemas import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    def __init__(self, repository: OrganizationRepository) -> None:
        self.repository = repository

    async def create_organization(self, payload: OrganizationCreate) -> Organization:
        email = payload.email.lower()
        if await self.repository.get_by_email(email):
            raise ConflictError("Organization with this email already exists", details={"email": email})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["email"] = email
        data.setdefault("status", OrganizationStatus.ACTIVE.value)
        if not data.get("display_name"):
            data["display_name"] = data["legal_name"]
        return await self.repository.create(data)

    async def list_organizations(self) -> list[Organization]:
        return await self.repository.list()

    async def get_organization(self, organization_id: UUID) -> Organization:
        organization = await self.repository.get_by_id(organization_id)
        if organization is None:
            raise NotFoundError("Organization not found", details={"id": str(organization_id)})
        return organization

    async def update_organization(
        self, organization_id: UUID, payload: OrganizationUpdate
    ) -> Organization:
        organization = await self.get_organization(organization_id)
        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"] is not None:
            email = str(data["email"]).lower()
            if email != organization.email and await self.repository.get_by_email(email):
                raise ConflictError("Organization with this email already exists", details={"email": email})
            data["email"] = email

        if "status" in data and data["status"] is not None:
            data["status"] = OrganizationStatus(data["status"]).value

        return await self.repository.update(organization, data)

    async def delete_organization(self, organization_id: UUID) -> Organization:
        organization = await self.get_organization(organization_id)
        return await self.repository.update(
            organization,
            {"status": OrganizationStatus.ARCHIVED.value},
        )
