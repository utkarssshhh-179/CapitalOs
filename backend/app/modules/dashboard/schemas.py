from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    organizations: int = 0
    borrowers: int = 0
    investors: int = 0
    loans: int = 0
    active_loans: int = 0
    payments: int = 0
    paid_payments: int = 0
    total_loan_value: float = 0.0
    total_paid_value: float = 0.0

    model_config = ConfigDict(from_attributes=True)
