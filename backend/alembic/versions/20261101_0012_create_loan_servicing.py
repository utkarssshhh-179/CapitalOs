"""Create loan servicing table

Revision ID: 20261101_0012
Revises: 20261101_0011
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0012"
down_revision = "20261101_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loan_servicing",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("loan_id", pg.UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("principal_outstanding", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0.00"),
        sa.Column("interest_outstanding", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0.00"),
        sa.Column("total_outstanding", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0.00"),
        sa.Column("next_due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("days_past_due", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_payment_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("last_payment_date", sa.DateTime(timezone=True), nullable=True),
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
            "status IN ('active','current','delinquent','defaulted','closed','restructured')",
            name="ck_loan_servicing_status",
        ),
        sa.UniqueConstraint("loan_id", name="uq_loan_servicing_loan_id"),
    )
    op.create_index("ix_loan_servicing_organization_id", "loan_servicing", ["organization_id"], unique=False)
    op.create_index("ix_loan_servicing_loan_id", "loan_servicing", ["loan_id"], unique=True)
    op.create_index("ix_loan_servicing_status", "loan_servicing", ["status"], unique=False)
    op.create_index("ix_loan_servicing_days_past_due", "loan_servicing", ["days_past_due"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_loan_servicing_days_past_due", table_name="loan_servicing")
    op.drop_index("ix_loan_servicing_status", table_name="loan_servicing")
    op.drop_index("ix_loan_servicing_loan_id", table_name="loan_servicing")
    op.drop_index("ix_loan_servicing_organization_id", table_name="loan_servicing")
    op.drop_table("loan_servicing")
