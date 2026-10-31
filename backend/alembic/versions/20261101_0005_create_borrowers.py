"""Create borrowers table

Revision ID: 20261101_0005
Revises: 20261029_0004
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261101_0005"
down_revision = "20261029_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "borrowers",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", pg.CITEXT(), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("pan_number", sa.String(length=20), nullable=True),
        sa.Column("aadhaar_number", sa.String(length=20), nullable=True),
        sa.Column("address_line1", sa.String(length=255), nullable=True),
        sa.Column("address_line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=False, server_default="India"),
        sa.Column("annual_income", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
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
        sa.CheckConstraint("status IN ('active', 'inactive', 'blacklisted', 'archived')", name="ck_borrowers_status"),
        sa.UniqueConstraint("organization_id", "email", name="uq_borrowers_org_email"),
    )
    op.create_index("ix_borrowers_organization_id", "borrowers", ["organization_id"], unique=False)
    op.create_index("ix_borrowers_email", "borrowers", ["email"], unique=False)
    op.create_index("ix_borrowers_status", "borrowers", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_borrowers_status", table_name="borrowers")
    op.drop_index("ix_borrowers_email", table_name="borrowers")
    op.drop_index("ix_borrowers_organization_id", table_name="borrowers")
    op.drop_table("borrowers")
