from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.permission import Permission
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.modules.auth.repository import PermissionRepository, RefreshTokenRepository, RoleRepository, UserRepository
from app.modules.auth.schemas import RefreshTokenRequest, TokenResponse, UserLogin, UserRegister, UserResponse


class AuthService:
    def __init__(self, session) -> None:
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.permission_repository = PermissionRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)

    async def register_user(self, payload: UserRegister, organization_id: UUID | None = None) -> User:
        email = str(payload.email).lower()
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise ConflictError("Account with this email already exists", details={"email": email})

        user = User(
            organization_id=organization_id,
            email=email,
            password_hash=hash_password(payload.password),
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            is_active=True,
            is_superuser=False,
        )
        await self.user_repository.create(user)
        if organization_id is not None:
            await self._ensure_default_membership(organization_id, user)
        return user

    async def login_user(self, payload: UserLogin) -> TokenResponse:
        email = str(payload.email).lower()
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise NotFoundError("Invalid email or password", details={"email": email})
        if not user.is_active:
            raise PermissionDeniedError("Account is disabled", details={"email": email})

        permissions = sorted({permission.name for role in user.roles for permission in role.permissions})
        access_token = create_access_token(
            str(user.id),
            organization_id=str(user.organization_id) if user.organization_id else None,
            permissions=permissions,
        )
        refresh_token_value = create_refresh_token(
            str(user.id),
            organization_id=str(user.organization_id) if user.organization_id else None,
        )
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token_value),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        await self.refresh_token_repository.create(refresh_token)
        user.last_login_at = datetime.now(UTC)
        await self.user_repository.update(user)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)

    async def refresh_access_token(self, payload: RefreshTokenRequest) -> TokenResponse:
        try:
            token_payload = decode_refresh_token(payload.refresh_token)
        except Exception as exc:
            raise PermissionDeniedError("Refresh token is invalid") from exc

        user_id = token_payload.get("sub")
        if not user_id:
            raise PermissionDeniedError("Refresh token payload is invalid")

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found", details={"id": str(user_id)})
        if not user.is_active:
            raise PermissionDeniedError("Account is disabled", details={"email": user.email})

        token_hash = hash_refresh_token(payload.refresh_token)
        stored_token = await self.refresh_token_repository.get_valid_by_hash(token_hash)
        if stored_token is None or stored_token.user_id != user.id:
            raise PermissionDeniedError("Refresh token is invalid or expired")

        permissions = sorted({permission.name for role in user.roles for permission in role.permissions})
        access_token = create_access_token(
            str(user.id),
            organization_id=str(user.organization_id) if user.organization_id else None,
            permissions=permissions,
        )
        new_refresh_token_value = create_refresh_token(
            str(user.id),
            organization_id=str(user.organization_id) if user.organization_id else None,
        )
        await self.refresh_token_repository.revoke(stored_token)
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token_value),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        await self.refresh_token_repository.create(new_refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token_value)

    async def get_current_user(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found", details={"id": str(user_id)})
        return user

    async def user_to_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            organization_id=user.organization_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[role.name for role in user.roles],
            permissions=sorted({permission.name for role in user.roles for permission in role.permissions}),
        )

    async def _ensure_default_membership(self, organization_id: UUID, user: User) -> None:
        existing_role = await self.role_repository.get_by_name(organization_id, "member")
        if existing_role is None:
            member_role = Role(
                organization_id=organization_id,
                name="member",
                description="Default user role",
            )
            default_permissions = [
                Permission(organization_id=organization_id, name="organization:read", description="Read organization info"),
                Permission(organization_id=organization_id, name="profile:read", description="Read own profile"),
            ]
            for permission in default_permissions:
                await self.permission_repository.create(permission)
                member_role.permissions.append(permission)
            await self.role_repository.create(member_role)
            existing_role = member_role
        user.roles.append(existing_role)
        await self.user_repository.update(user)
