"""Create underwriting reviews table

Revision ID: 20261101_0013
Revises: 20261101_0012
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0013"
down_revision = "20261101_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "underwriting_reviews",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("loan_id", pg.UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("reviewer_user_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_band", sa.String(length=20), nullable=True),
        sa.Column("recommended_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("approved_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("rationale", sa.String(length=1000), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
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
            "status IN ('pending','approved','rejected','manual_review','conditional')",
            name="ck_underwriting_reviews_status",
        ),
        sa.UniqueConstraint("loan_id", name="uq_underwriting_reviews_loan_id"),
    )
    op.create_index("ix_underwriting_reviews_organization_id", "underwriting_reviews", ["organization_id"], unique=False)
    op.create_index("ix_underwriting_reviews_loan_id", "underwriting_reviews", ["loan_id"], unique=True)
    op.create_index("ix_underwriting_reviews_reviewer_user_id", "underwriting_reviews", ["reviewer_user_id"], unique=False)
    op.create_index("ix_underwriting_reviews_status", "underwriting_reviews", ["status"], unique=False)
    op.create_index("ix_underwriting_reviews_risk_score", "underwriting_reviews", ["risk_score"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_underwriting_reviews_risk_score", table_name="underwriting_reviews")
    op.drop_index("ix_underwriting_reviews_status", table_name="underwriting_reviews")
    op.drop_index("ix_underwriting_reviews_reviewer_user_id", table_name="underwriting_reviews")
    op.drop_index("ix_underwriting_reviews_loan_id", table_name="underwriting_reviews")
    op.drop_index("ix_underwriting_reviews_organization_id", table_name="underwriting_reviews")
    op.drop_table("underwriting_reviews")
