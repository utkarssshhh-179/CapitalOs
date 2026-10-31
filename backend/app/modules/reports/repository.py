from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrower import Borrower
from app.models.investor import Investor
from app.models.loan import Loan, LoanStatus
from app.models.loan_servicing import LoanServicing, LoanServicingStatus
from app.models.organization import Organization
from app.models.payment import Payment, PaymentStatus


class ReportsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_portfolio_report(self, organization_id: UUID | None = None) -> dict[str, int | float | str | None]:
        org_filter = Organization.id == organization_id if organization_id is not None else None
        borrower_filter = Borrower.organization_id == organization_id if organization_id is not None else None
        investor_filter = Investor.organization_id == organization_id if organization_id is not None else None
        loan_filter = Loan.organization_id == organization_id if organization_id is not None else None
        payment_filter = Payment.organization_id == organization_id if organization_id is not None else None

        total_organizations = await self.session.scalar(select(func.count()).select_from(Organization)) or 0
        total_borrowers = await self.session.scalar(
            select(func.count()).select_from(Borrower).where(borrower_filter) if borrower_filter is not None else select(func.count()).select_from(Borrower)
        ) or 0
        total_investors = await self.session.scalar(
            select(func.count()).select_from(Investor).where(investor_filter) if investor_filter is not None else select(func.count()).select_from(Investor)
        ) or 0
        total_loans = await self.session.scalar(
            select(func.count()).select_from(Loan).where(loan_filter) if loan_filter is not None else select(func.count()).select_from(Loan)
        ) or 0
        active_loans = await self.session.scalar(
            select(func.count()).select_from(Loan).where((Loan.status == LoanStatus.ACTIVE.value) if loan_filter is None else (loan_filter & (Loan.status == LoanStatus.ACTIVE.value)))
        ) or 0
        delinquent_loans = await self.session.scalar(
            select(func.count()).select_from(LoanServicing).where(
                (LoanServicing.status.in_([LoanServicingStatus.DELINQUENT.value, LoanServicingStatus.DEFAULTED.value]))
                if organization_id is None
                else (LoanServicing.organization_id == organization_id) & (LoanServicing.status.in_([LoanServicingStatus.DELINQUENT.value, LoanServicingStatus.DEFAULTED.value]))
            )
        ) or 0
        total_disbursed = await self.session.scalar(
            select(func.coalesce(func.sum(Loan.principal_amount), 0.0)).select_from(Loan).where(loan_filter) if loan_filter is not None else select(func.coalesce(func.sum(Loan.principal_amount), 0.0)).select_from(Loan)
        ) or 0.0
        total_collected = await self.session.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).select_from(Payment).where((Payment.status == PaymentStatus.PAID.value) if payment_filter is None else (payment_filter & (Payment.status == PaymentStatus.PAID.value)))
        ) or 0.0
        outstanding_balance = float(total_disbursed) - float(total_collected)
        average_loan_size = float(total_disbursed) / float(total_loans) if total_loans else 0.0

        return {
            "organization_id": str(organization_id) if organization_id is not None else None,
            "total_organizations": int(total_organizations),
            "total_borrowers": int(total_borrowers),
            "total_investors": int(total_investors),
            "total_loans": int(total_loans),
            "active_loans": int(active_loans),
            "delinquent_loans": int(delinquent_loans),
            "total_disbursed": float(total_disbursed),
            "total_collected": float(total_collected),
            "outstanding_balance": float(outstanding_balance),
            "average_loan_size": float(average_loan_size),
        }
