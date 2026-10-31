from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.borrower import Borrower, BorrowerStatus
from app.modules.borrower.repository import BorrowerRepository
from app.modules.borrower.schemas import BorrowerCreate, BorrowerUpdate


class BorrowerService:
    def __init__(self, repository: BorrowerRepository) -> None:
        self.repository = repository

    async def create_borrower(self, payload: BorrowerCreate) -> Borrower:
        organization_id = payload.organization_id
        if organization_id is None:
            raise ValueError("organization_id is required to create a borrower")

        email = str(payload.email).lower()
        existing = await self.repository.get_by_email_and_organization(organization_id, email)
        if existing is not None:
            raise ConflictError("Borrower with this email already exists in the organization", details={"email": email})

        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["organization_id"] = organization_id
        data["email"] = email
        data.setdefault("status", BorrowerStatus.ACTIVE.value)
        return await self.repository.create(data)

    async def list_borrowers(self, organization_id: UUID | None = None) -> list[Borrower]:
        if organization_id is None:
            return await self.repository.list()
        return await self.repository.list_by_organization(organization_id)

    async def get_borrower(self, borrower_id: UUID) -> Borrower:
        borrower = await self.repository.get_by_id(borrower_id)
        if borrower is None:
            raise NotFoundError("Borrower not found", details={"id": str(borrower_id)})
        return borrower

    async def update_borrower(self, borrower_id: UUID, payload: BorrowerUpdate) -> Borrower:
        borrower = await self.get_borrower(borrower_id)
        data = payload.model_dump(exclude_unset=True)

        if "email" in data and data["email"] is not None:
            email = str(data["email"]).lower()
            if email != borrower.email and await self.repository.get_by_email_and_organization(borrower.organization_id, email):
                raise ConflictError("Borrower with this email already exists in the organization", details={"email": email})
            data["email"] = email

        if "status" in data and data["status"] is not None:
            data["status"] = BorrowerStatus(data["status"]).value

        return await self.repository.update(borrower, data)

    async def archive_borrower(self, borrower_id: UUID) -> Borrower:
        borrower = await self.get_borrower(borrower_id)
        return await self.repository.update(borrower, {"status": BorrowerStatus.ARCHIVED.value})
