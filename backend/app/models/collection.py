from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CollectionStatus(StrEnum):
    OPEN = "open"
    CONTACTED = "contacted"
    PROMISED = "promised"
    RESOLVED = "resolved"
    FAILED = "failed"


class Collection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "collections"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    loan_id: Mapped[UUID] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    borrower_id: Mapped[UUID] = mapped_column(ForeignKey("borrowers.id"), nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CollectionStatus.OPEN.value,
        server_default=CollectionStatus.OPEN.value,
        index=True,
    )
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
