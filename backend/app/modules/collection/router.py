from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.collection.repository import CollectionRepository
from app.modules.collection.schemas import CollectionCreate, CollectionResponse, CollectionUpdate
from app.modules.collection.service import CollectionService

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[CollectionResponse]:
    service = CollectionService(CollectionRepository(session))
    return await service.list_collections(organization_id)


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CollectionResponse:
    service = CollectionService(CollectionRepository(session))
    return await service.get_collection(collection_id)


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CollectionResponse:
    service = CollectionService(CollectionRepository(session))
    return await service.create_collection(payload)


@router.patch("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: UUID,
    payload: CollectionUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CollectionResponse:
    service = CollectionService(CollectionRepository(session))
    return await service.update_collection(collection_id, payload)


@router.delete("/{collection_id}", response_model=CollectionResponse)
async def resolve_collection(
    collection_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CollectionResponse:
    service = CollectionService(CollectionRepository(session))
    return await service.resolve_collection(collection_id)
