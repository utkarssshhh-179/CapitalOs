from __future__ import annotations

import uuid

import pytest

from app.modules.reports.schemas import PortfolioReport
from app.modules.reports.service import ReportsService


class FakeReportsRepository:
    async def get_portfolio_report(self, organization_id: uuid.UUID | None = None) -> dict[str, object]:
        return {
            "organization_id": str(organization_id) if organization_id is not None else None,
            "total_organizations": 3,
            "total_borrowers": 10,
            "total_investors": 4,
            "total_loans": 8,
            "active_loans": 6,
            "delinquent_loans": 2,
            "total_disbursed": 150000.0,
            "total_collected": 90000.0,
            "outstanding_balance": 60000.0,
            "average_loan_size": 18750.0,
        }


@pytest.mark.asyncio
async def test_reports_service_builds_portfolio_report() -> None:
    service = ReportsService(FakeReportsRepository())

    report = await service.get_portfolio_report(uuid.uuid4())

    assert isinstance(report, PortfolioReport)
    assert report.total_loans == 8
    assert report.active_loans == 6
    assert report.delinquent_loans == 2
    assert report.outstanding_balance == 60000.0
    assert report.average_loan_size == 18750.0


@pytest.mark.asyncio
async def test_reports_service_supports_global_view() -> None:
    service = ReportsService(FakeReportsRepository())

    report = await service.get_portfolio_report()

    assert report.organization_id is None
    assert report.total_organizations == 3
