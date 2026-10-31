from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schemas import PortfolioReport
from app.modules.reports.service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/portfolio", response_model=PortfolioReport)
async def get_portfolio_report(
    session: Annotated[AsyncSession, Depends(get_session)],
    organization_id: UUID | None = None,
) -> PortfolioReport:
    service = ReportsService(ReportsRepository(session))
    return await service.get_portfolio_report(organization_id)
