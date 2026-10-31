from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PortfolioReport(BaseModel):
    organization_id: str | None = None
    total_organizations: int = 0
    total_borrowers: int = 0
    total_investors: int = 0
    total_loans: int = 0
    active_loans: int = 0
    delinquent_loans: int = 0
    total_disbursed: float = 0.0
    total_collected: float = 0.0
    outstanding_balance: float = 0.0
    average_loan_size: float = 0.0

    model_config = ConfigDict(from_attributes=True)
