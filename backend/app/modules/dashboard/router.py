from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import DashboardSummary
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
async def get_dashboard_summary(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DashboardSummary:
    service = DashboardService(DashboardRepository(session))
    return await service.get_summary()
