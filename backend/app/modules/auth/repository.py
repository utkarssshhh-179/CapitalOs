from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Permission
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID | str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        await self.session.flush()
        return user


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, organization_id: UUID, name: str) -> Role | None:
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.organization_id == organization_id, Role.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        return role


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, organization_id: UUID, name: str) -> Permission | None:
        result = await self.session.execute(
            select(Permission).where(Permission.organization_id == organization_id, Permission.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.flush()
        return permission


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_valid_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
            .where(RefreshToken.expires_at > datetime.now(UTC))
        )
        return result.scalar_one_or_none()

    async def revoke_by_user(self, user_id: UUID) -> None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))
        for token in result.scalars().all():
            token.revoked = True
        await self.session.flush()

    async def revoke(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.revoked = True
        await self.session.flush()
        return refresh_token
