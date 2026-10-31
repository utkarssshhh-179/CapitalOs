from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.payment.repository import PaymentRepository
from app.modules.payment.schemas import PaymentCreate, PaymentResponse, PaymentUpdate
from app.modules.payment.service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[PaymentResponse])
async def list_payments(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> list[PaymentResponse]:
    service = PaymentService(PaymentRepository(session))
    return await service.list_payments(organization_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(session))
    return await service.get_payment(payment_id)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(session))
    return await service.create_payment(payload)


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    payload: PaymentUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(session))
    return await service.update_payment(payment_id, payload)


@router.delete("/{payment_id}", response_model=PaymentResponse)
async def mark_paid(
    payment_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(session))
    return await service.mark_payment_paid(payment_id)
