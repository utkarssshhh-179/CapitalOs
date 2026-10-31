"""Create loans table

Revision ID: 20261101_0007
Revises: 20261101_0006
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0007"
down_revision = "20261101_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loans",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("borrower_id", pg.UUID(as_uuid=True), sa.ForeignKey("borrowers.id"), nullable=False),
        sa.Column("investor_id", pg.UUID(as_uuid=True), sa.ForeignKey("investors.id"), nullable=False),
        sa.Column("loan_number", sa.String(length=50), nullable=False),
        sa.Column("principal_amount", sa.Float(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("tenure_months", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("disbursed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("maturity_date", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint("status IN ('pending','approved','disbursed','active','closed','defaulted')", name="ck_loans_status"),
        sa.UniqueConstraint("loan_number", name="uq_loans_number"),
    )
    op.create_index("ix_loans_organization_id", "loans", ["organization_id"], unique=False)
    op.create_index("ix_loans_borrower_id", "loans", ["borrower_id"], unique=False)
    op.create_index("ix_loans_investor_id", "loans", ["investor_id"], unique=False)
    op.create_index("ix_loans_status", "loans", ["status"], unique=False)
    op.create_index("ix_loans_loan_number", "loans", ["loan_number"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_loans_loan_number", table_name="loans")
    op.drop_index("ix_loans_status", table_name="loans")
    op.drop_index("ix_loans_investor_id", table_name="loans")
    op.drop_index("ix_loans_borrower_id", table_name="loans")
    op.drop_index("ix_loans_organization_id", table_name="loans")
    op.drop_table("loans")
