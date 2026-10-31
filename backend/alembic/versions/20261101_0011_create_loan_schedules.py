"""Create loan schedules table

Revision ID: 20261101_0011
Revises: 20261101_0010
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0011"
down_revision = "20261101_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loan_schedules",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("loan_id", pg.UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("installment_number", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("principal_component", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("interest_component", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_installment", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('scheduled','paid','partial','overdue','skipped')",
            name="ck_loan_schedules_status",
        ),
        sa.UniqueConstraint("loan_id", "installment_number", name="uq_loan_schedules_loan_installment"),
    )
    op.create_index("ix_loan_schedules_organization_id", "loan_schedules", ["organization_id"], unique=False)
    op.create_index("ix_loan_schedules_loan_id", "loan_schedules", ["loan_id"], unique=False)
    op.create_index("ix_loan_schedules_installment_number", "loan_schedules", ["installment_number"], unique=False)
    op.create_index("ix_loan_schedules_due_date", "loan_schedules", ["due_date"], unique=False)
    op.create_index("ix_loan_schedules_status", "loan_schedules", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_loan_schedules_status", table_name="loan_schedules")
    op.drop_index("ix_loan_schedules_due_date", table_name="loan_schedules")
    op.drop_index("ix_loan_schedules_installment_number", table_name="loan_schedules")
    op.drop_index("ix_loan_schedules_loan_id", table_name="loan_schedules")
    op.drop_index("ix_loan_schedules_organization_id", table_name="loan_schedules")
    op.drop_table("loan_schedules")
