"""Create organizations table

Revision ID: 20261029_0002
Revises: 0001
Create Date: 2026-10-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "20261029_0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("registration_number", sa.String(length=100), nullable=True),
        sa.Column("gst_number", sa.String(length=50), nullable=True),
        sa.Column("pan_number", sa.String(length=20), nullable=True),
        sa.Column("email", pg.CITEXT(), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("country", sa.String(length=64), nullable=False, server_default="India"),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
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
        sa.CheckConstraint("status IN ('active', 'suspended', 'archived')", name="ck_organizations_status"),
    )
    op.create_index("ix_organizations_registration_number", "organizations", ["registration_number"], unique=False)
    op.create_index("ix_organizations_status", "organizations", ["status"], unique=False)
    op.create_index("ix_organizations_email", "organizations", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_organizations_email", table_name="organizations")
    op.drop_index("ix_organizations_status", table_name="organizations")
    op.drop_index("ix_organizations_registration_number", table_name="organizations")
    op.drop_table("organizations")
