from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import hash_password
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.modules.auth.repository import RefreshTokenRepository
from app.modules.auth.schemas import RefreshTokenRequest, UserLogin
from app.modules.auth.service import AuthService


class FakeUserRepository:
    def __init__(self, users: dict[str, User] | None = None) -> None:
        self.users = users or {}

    async def get_by_email(self, email: str) -> User | None:
        return self.users.get(email)

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        user_id_str = str(user_id)
        for user in self.users.values():
            if str(user.id) == user_id_str:
                return user
        return None

    async def create(self, user: User) -> User:
        self.users[user.email] = user
        return user

    async def update(self, user: User) -> User:
        self.users[user.email] = user
        return user


class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self.tokens: dict[str, object] = {}

    async def create(self, refresh_token: object) -> object:
        self.tokens[refresh_token.token_hash] = refresh_token
        return refresh_token

    async def get_valid_by_hash(self, token_hash: str) -> object | None:
        token = self.tokens.get(token_hash)
        if token is not None and not token.revoked and token.expires_at > datetime.now(UTC):
            return token
        return None

    async def revoke(self, refresh_token: object) -> object:
        refresh_token.revoked = True
        return refresh_token


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens() -> None:
    user = User(
        id=uuid.uuid4(),
        email="owner@capitalos.io",
        password_hash=hash_password("secret123"),
        first_name="Ada",
        last_name="Lovelace",
        is_active=True,
        is_superuser=False,
    )
    role = Role(id=uuid.uuid4(), organization_id=uuid.uuid4(), name="owner", description="Owner")
    permission = Permission(id=uuid.uuid4(), organization_id=role.organization_id, name="organization:read", description="Read")
    role.permissions = [permission]
    user.roles = [role]

    service = AuthService(session=None)
    service.user_repository = FakeUserRepository({user.email: user})
    service.refresh_token_repository = FakeRefreshTokenRepository()

    token = await service.login_user(UserLogin(email="owner@capitalos.io", password="secret123"))

    assert token.access_token
    assert token.refresh_token
    assert token.access_token != token.refresh_token


@pytest.mark.asyncio
async def test_refresh_token_rotates_access_token() -> None:
    user = User(
        id=uuid.uuid4(),
        email="owner@capitalos.io",
        password_hash=hash_password("secret123"),
        first_name="Ada",
        last_name="Lovelace",
        is_active=True,
        is_superuser=False,
    )
    role = Role(id=uuid.uuid4(), organization_id=uuid.uuid4(), name="owner", description="Owner")
    permission = Permission(id=uuid.uuid4(), organization_id=role.organization_id, name="organization:read", description="Read")
    role.permissions = [permission]
    user.roles = [role]

    service = AuthService(session=None)
    service.user_repository = FakeUserRepository({user.email: user})
    service.refresh_token_repository = FakeRefreshTokenRepository()

    login = await service.login_user(UserLogin(email="owner@capitalos.io", password="secret123"))
    refreshed = await service.refresh_access_token(RefreshTokenRequest(refresh_token=login.refresh_token))

    assert refreshed.access_token
    assert refreshed.refresh_token
    assert refreshed.access_token != login.access_token
    assert refreshed.refresh_token != login.refresh_token
