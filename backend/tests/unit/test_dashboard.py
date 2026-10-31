from __future__ import annotations

import pytest

from app.modules.dashboard.schemas import DashboardSummary
from app.modules.dashboard.service import DashboardService


class FakeDashboardRepository:
    async def get_summary(self) -> dict[str, int | float]:
        return {
            "organizations": 4,
            "borrowers": 12,
            "investors": 3,
            "loans": 9,
            "active_loans": 5,
            "payments": 16,
            "paid_payments": 11,
            "total_loan_value": 1245000.0,
            "total_paid_value": 780000.0,
        }


@pytest.mark.asyncio
async def test_dashboard_summary_builds_expected_totals() -> None:
    service = DashboardService(FakeDashboardRepository())

    summary = await service.get_summary()

    assert isinstance(summary, DashboardSummary)
    assert summary.organizations == 4
    assert summary.borrowers == 12
    assert summary.investors == 3
    assert summary.loans == 9
    assert summary.active_loans == 5
    assert summary.payments == 16
    assert summary.paid_payments == 11
    assert summary.total_loan_value == 1245000.0
    assert summary.total_paid_value == 780000.0
