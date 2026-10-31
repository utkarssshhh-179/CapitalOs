"""Create ledger entries table

Revision ID: 20261101_0010
Revises: 20261101_0009
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0010"
down_revision = "20261101_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ledger_entries",
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
        sa.Column("entry_number", sa.String(length=50), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False, server_default="payment"),
        sa.Column("direction", sa.String(length=10), nullable=False, server_default="debit"),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("reversal_of_id", pg.UUID(as_uuid=True), sa.ForeignKey("ledger_entries.id"), nullable=True),
        sa.Column("related_payment_id", pg.UUID(as_uuid=True), sa.ForeignKey("payments.id"), nullable=True),
        sa.Column("related_collection_id", pg.UUID(as_uuid=True), sa.ForeignKey("collections.id"), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
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
            "entry_type IN ('disbursement','payment','accrual','penalty','fee','reversal')",
            name="ck_ledger_entries_entry_type",
        ),
        sa.CheckConstraint("direction IN ('debit','credit')", name="ck_ledger_entries_direction"),
        sa.UniqueConstraint("entry_number", name="uq_ledger_entries_entry_number"),
    )
    op.create_index("ix_ledger_entries_organization_id", "ledger_entries", ["organization_id"], unique=False)
    op.create_index("ix_ledger_entries_loan_id", "ledger_entries", ["loan_id"], unique=False)
    op.create_index("ix_ledger_entries_borrower_id", "ledger_entries", ["borrower_id"], unique=False)
    op.create_index("ix_ledger_entries_entry_type", "ledger_entries", ["entry_type"], unique=False)
    op.create_index("ix_ledger_entries_direction", "ledger_entries", ["direction"], unique=False)
    op.create_index("ix_ledger_entries_entry_number", "ledger_entries", ["entry_number"], unique=True)
    op.create_index("ix_ledger_entries_reversal_of_id", "ledger_entries", ["reversal_of_id"], unique=False)
    op.create_index("ix_ledger_entries_related_payment_id", "ledger_entries", ["related_payment_id"], unique=False)
    op.create_index("ix_ledger_entries_related_collection_id", "ledger_entries", ["related_collection_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_related_collection_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_related_payment_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_reversal_of_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_entry_number", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_direction", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_entry_type", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_borrower_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_loan_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_organization_id", table_name="ledger_entries")
    op.drop_table("ledger_entries")
