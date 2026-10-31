from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BorrowerStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    ARCHIVED = "archived"


class Borrower(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "borrowers"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_borrowers_org_email"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(64), nullable=False, server_default="India")
    annual_income: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=BorrowerStatus.ACTIVE.value,
        server_default=BorrowerStatus.ACTIVE.value,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
