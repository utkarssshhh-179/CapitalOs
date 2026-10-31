from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.organization.repository import OrganizationRepository
from app.modules.organization.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.modules.organization.service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[OrganizationResponse]:
    service = OrganizationService(OrganizationRepository(session))
    return await service.list_organizations()


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationResponse:
    service = OrganizationService(OrganizationRepository(session))
    return await service.get_organization(organization_id)


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationResponse:
    service = OrganizationService(OrganizationRepository(session))
    return await service.create_organization(payload)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationResponse:
    service = OrganizationService(OrganizationRepository(session))
    return await service.update_organization(organization_id, payload)


@router.delete("/{organization_id}", response_model=OrganizationResponse)
async def delete_organization(
    organization_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationResponse:
    service = OrganizationService(OrganizationRepository(session))
    return await service.delete_organization(organization_id)
