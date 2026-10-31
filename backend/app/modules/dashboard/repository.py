from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrower import Borrower
from app.models.investor import Investor
from app.models.loan import Loan, LoanStatus
from app.models.organization import Organization
from app.models.payment import Payment, PaymentStatus


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_summary(self) -> dict[str, int | float]:
        organizations = await self.session.scalar(select(func.count()).select_from(Organization)) or 0
        borrowers = await self.session.scalar(select(func.count()).select_from(Borrower)) or 0
        investors = await self.session.scalar(select(func.count()).select_from(Investor)) or 0
        loans = await self.session.scalar(select(func.count()).select_from(Loan)) or 0
        active_loans = await self.session.scalar(
            select(func.count()).select_from(Loan).where(Loan.status == LoanStatus.ACTIVE.value)
        ) or 0
        payments = await self.session.scalar(select(func.count()).select_from(Payment)) or 0
        paid_payments = await self.session.scalar(
            select(func.count()).select_from(Payment).where(Payment.status == PaymentStatus.PAID.value)
        ) or 0
        total_loan_value = await self.session.scalar(
            select(func.coalesce(func.sum(Loan.principal_amount), 0.0)).select_from(Loan)
        ) or 0.0
        total_paid_value = await self.session.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).select_from(Payment).where(Payment.status == PaymentStatus.PAID.value)
        ) or 0.0

        return {
            "organizations": int(organizations),
            "borrowers": int(borrowers),
            "investors": int(investors),
            "loans": int(loans),
            "active_loans": int(active_loans),
            "payments": int(payments),
            "paid_payments": int(paid_payments),
            "total_loan_value": float(total_loan_value),
            "total_paid_value": float(total_paid_value),
        }
