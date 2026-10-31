from __future__ import annotations

from uuid import UUID

from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schemas import PortfolioReport


class ReportsService:
    def __init__(self, repository: ReportsRepository) -> None:
        self.repository = repository

    async def get_portfolio_report(self, organization_id: UUID | None = None) -> PortfolioReport:
        payload = await self.repository.get_portfolio_report(organization_id)
        return PortfolioReport(**payload)
