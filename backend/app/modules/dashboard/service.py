from __future__ import annotations

from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import DashboardSummary


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    async def get_summary(self) -> DashboardSummary:
        payload = await self.repository.get_summary()
        return DashboardSummary(**payload)
