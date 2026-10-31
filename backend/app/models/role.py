from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base import Base
from app.db.mixins import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.association import role_permissions, user_roles


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions = relationship("Permission", secondary=role_permissions, backref="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_roles_organization_name"),
    )
