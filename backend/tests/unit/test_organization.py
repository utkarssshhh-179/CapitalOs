from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions import ConflictError
from app.models.organization import Organization, OrganizationStatus
from app.modules.organization.schemas import OrganizationCreate, OrganizationUpdate
from app.modules.organization.service import OrganizationService


class FakeOrganizationRepository:
    def __init__(self) -> None:
        self.items: dict[str, Organization] = {}

    async def create(self, data: dict[str, object]) -> Organization:
        organization = Organization(**data)
        organization.id = uuid.uuid4()
        organization.created_at = datetime.now(UTC)
        organization.updated_at = organization.created_at
        self.items[organization.email] = organization
        return organization

    async def get_by_email(self, email: str) -> Organization | None:
        return self.items.get(email)

    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        for organization in self.items.values():
            if organization.id == organization_id:
                return organization
        return None

    async def list(self) -> list[Organization]:
        return list(self.items.values())

    async def update(self, organization: Organization, data: dict[str, object]) -> Organization:
        for key, value in data.items():
            setattr(organization, key, value)
        organization.updated_at = datetime.now(UTC)
        self.items[organization.email] = organization
        return organization


@pytest.mark.asyncio
async def test_create_organization_succeeds() -> None:
    service = OrganizationService(FakeOrganizationRepository())

    organization = await service.create_organization(
        OrganizationCreate(
            legal_name="Acme Finance",
            display_name="Acme",
            email="hello@acme.example",
        )
    )

    assert organization.legal_name == "Acme Finance"
    assert organization.email == "hello@acme.example"
    assert organization.status == OrganizationStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_create_organization_rejects_duplicate_email() -> None:
    repository = FakeOrganizationRepository()
    service = OrganizationService(repository)

    await service.create_organization(
        OrganizationCreate(
            legal_name="Acme Finance",
            display_name="Acme",
            email="hello@acme.example",
        )
    )

    with pytest.raises(ConflictError, match="already exists"):
        await service.create_organization(
            OrganizationCreate(
                legal_name="Another Finance",
                display_name="Another",
                email="HELLO@acme.example",
            )
        )


@pytest.mark.asyncio
async def test_update_organization_changes_email_and_status() -> None:
    repository = FakeOrganizationRepository()
    service = OrganizationService(repository)
    organization = await service.create_organization(
        OrganizationCreate(
            legal_name="Acme Finance",
            display_name="Acme",
            email="hello@acme.example",
        )
    )

    updated = await service.update_organization(
        organization.id,
        OrganizationUpdate(email="updated@acme.example", status=OrganizationStatus.SUSPENDED),
    )

    assert updated.email == "updated@acme.example"
    assert updated.status == OrganizationStatus.SUSPENDED.value
