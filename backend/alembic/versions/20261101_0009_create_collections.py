"""Create collections table

Revision ID: 20261101_0009
Revises: 20261101_0008
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0009"
down_revision = "20261101_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collections",
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
        sa.Column("case_number", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("follow_up_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint("status IN ('open','contacted','promised','resolved','failed')", name="ck_collections_status"),
        sa.UniqueConstraint("case_number", name="uq_collections_case_number"),
    )
    op.create_index("ix_collections_organization_id", "collections", ["organization_id"], unique=False)
    op.create_index("ix_collections_loan_id", "collections", ["loan_id"], unique=False)
    op.create_index("ix_collections_borrower_id", "collections", ["borrower_id"], unique=False)
    op.create_index("ix_collections_status", "collections", ["status"], unique=False)
    op.create_index("ix_collections_case_number", "collections", ["case_number"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_collections_case_number", table_name="collections")
    op.drop_index("ix_collections_status", table_name="collections")
    op.drop_index("ix_collections_borrower_id", table_name="collections")
    op.drop_index("ix_collections_loan_id", table_name="collections")
    op.drop_index("ix_collections_organization_id", table_name="collections")
    op.drop_table("collections")
