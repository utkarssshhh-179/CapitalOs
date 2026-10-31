from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.investor import Investor, InvestorStatus
from app.modules.investor.repository import InvestorRepository
from app.modules.investor.schemas import InvestorCreate, InvestorUpdate


class InvestorService:
    def __init__(self, repository: InvestorRepository) -> None:
        self.repository = repository

    async def create_investor(self, payload: InvestorCreate) -> Investor:
        organization_id = payload.organization_id
        if organization_id is None:
            raise ValueError("organization_id is required to create an investor")

        email = str(payload.email).lower()
        existing = await self.repository.get_by_email_and_organization(organization_id, email)
        if existing is not None:
            raise ConflictError("Investor with this email already exists in the organization", details={"email": email})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["organization_id"] = organization_id
        data["email"] = email
        data.setdefault("status", InvestorStatus.ACTIVE.value)
        return await self.repository.create(data)

    async def list_investors(self, organization_id: UUID | None = None) -> list[Investor]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_investor(self, investor_id: UUID) -> Investor:
        investor = await self.repository.get_by_id(investor_id)
        if investor is None:
            raise NotFoundError("Investor not found", details={"id": str(investor_id)})
        return investor

    async def update_investor(self, investor_id: UUID, payload: InvestorUpdate) -> Investor:
        investor = await self.get_investor(investor_id)
        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"] is not None:
            email = str(data["email"]).lower()
            if email != investor.email and await self.repository.get_by_email_and_organization(investor.organization_id, email):
                raise ConflictError("Investor with this email already exists in the organization", details={"email": email})
            data["email"] = email

        if "status" in data and data["status"] is not None:
            data["status"] = InvestorStatus(data["status"]).value

        return await self.repository.update(investor, data)

    async def archive_investor(self, investor_id: UUID) -> Investor:
        investor = await self.get_investor(investor_id)
        return await self.repository.update(investor, {"status": InvestorStatus.ARCHIVED.value})
