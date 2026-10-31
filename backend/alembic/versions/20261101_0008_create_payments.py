"""Create payments table

Revision ID: 20261101_0008
Revises: 20261101_0007
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0008"
down_revision = "20261101_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("loan_id", pg.UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("borrower_id", pg.UUID(as_uuid=True), sa.ForeignKey("borrowers.id"), nullable=False),
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_mode", sa.String(length=30), nullable=False, server_default="bank_transfer"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reference_code", sa.String(length=100), nullable=True),
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
        sa.CheckConstraint("status IN ('pending','paid','partial','failed','reversed')", name="ck_payments_status"),
        sa.UniqueConstraint("payment_number", name="uq_payments_number"),
    )
    op.create_index("ix_payments_organization_id", "payments", ["organization_id"], unique=False)
    op.create_index("ix_payments_loan_id", "payments", ["loan_id"], unique=False)
    op.create_index("ix_payments_borrower_id", "payments", ["borrower_id"], unique=False)
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index("ix_payments_payment_number", "payments", ["payment_number"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_payments_payment_number", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_borrower_id", table_name="payments")
    op.drop_index("ix_payments_loan_id", table_name="payments")
    op.drop_index("ix_payments_organization_id", table_name="payments")
    op.drop_table("payments")
