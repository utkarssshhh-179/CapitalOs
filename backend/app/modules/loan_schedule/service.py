from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.core.money import ZERO, to_money
from app.models.loan_schedule import LoanSchedule, LoanScheduleStatus
from app.modules.loan_schedule.repository import LoanScheduleRepository
from app.modules.loan_schedule.schemas import LoanScheduleCreate, LoanScheduleUpdate


class LoanScheduleService:
    def __init__(self, repository: LoanScheduleRepository) -> None:
        self.repository = repository

    async def create_schedule_entry(self, payload: LoanScheduleCreate) -> LoanSchedule:
        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        data["principal_component"] = to_money(data["principal_component"])
        data["interest_component"] = to_money(data["interest_component"])
        data["total_installment"] = to_money(data["total_installment"])
        data.setdefault("status", LoanScheduleStatus.SCHEDULED.value)
        if data["total_installment"] <= ZERO:
            raise ConflictError("Total installment must be greater than zero")
        return await self.repository.create(data)

    async def list_schedule_entries(self, loan_id: UUID | None = None, organization_id: UUID | None = None) -> list[LoanSchedule]:
        if loan_id is not None:
            return await self.repository.list_by_loan(loan_id)
        if organization_id is not None:
            return await self.repository.list_by_organization(organization_id)
        return await self.repository.list()

    async def get_schedule_entry(self, schedule_id: UUID) -> LoanSchedule:
        schedule = await self.repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundError("Loan schedule entry not found", details={"id": str(schedule_id)})
        return schedule

    async def update_schedule_entry(self, schedule_id: UUID, payload: LoanScheduleUpdate) -> LoanSchedule:
        schedule = await self.get_schedule_entry(schedule_id)
        data = payload.model_dump(exclude_unset=True)

        if "principal_component" in data and data["principal_component"] is not None:
            data["principal_component"] = to_money(data["principal_component"])
        if "interest_component" in data and data["interest_component"] is not None:
            data["interest_component"] = to_money(data["interest_component"])
        if "total_installment" in data and data["total_installment"] is not None:
            data["total_installment"] = to_money(data["total_installment"])
        if "status" in data and data["status"] is not None:
            data["status"] = LoanScheduleStatus(data["status"]).value

        return await self.repository.update(schedule, data)

    def generate_schedule(
        self,
        *,
        organization_id: UUID,
        loan_id: UUID,
        principal_amount: Decimal | int | str,
        annual_interest_rate: Decimal | int | str,
        tenure_months: int,
        start_date: datetime | None = None,
    ) -> list[LoanSchedule]:
        if tenure_months <= 0:
            raise ValueError("tenure_months must be greater than zero")

        principal = to_money(principal_amount)
        annual_rate = Decimal(str(annual_interest_rate))
        monthly_rate = annual_rate / Decimal("1200")

        if monthly_rate > ZERO:
            emi = principal * monthly_rate / (Decimal("1") - (Decimal("1") + monthly_rate) ** (-tenure_months))
        else:
            emi = principal / Decimal(tenure_months)

        emi = emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        remaining_balance = principal
        generated: list[LoanSchedule] = []
        current_date = start_date or datetime.now(UTC)

        for installment_number in range(1, tenure_months + 1):
            interest = (remaining_balance * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if installment_number == tenure_months:
                principal_component = remaining_balance
                total_installment = remaining_balance + interest
            else:
                principal_component = (emi - interest).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_installment = emi
            remaining_balance = (remaining_balance - principal_component).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if remaining_balance < ZERO:
                remaining_balance = ZERO

            due_date = current_date
            generated.append(
                LoanSchedule(
                    organization_id=organization_id,
                    loan_id=loan_id,
                    installment_number=installment_number,
                    due_date=due_date,
                    principal_component=principal_component,
                    interest_component=interest,
                    total_installment=total_installment,
                    status=LoanScheduleStatus.SCHEDULED.value,
                )
            )
            current_date = datetime.fromtimestamp(current_date.timestamp() + 30 * 24 * 60 * 60)

        return generated
