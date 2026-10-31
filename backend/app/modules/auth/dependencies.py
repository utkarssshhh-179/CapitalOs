from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User
from app.modules.auth.repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session=Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:  # pragma: no cover - library raises jwt exceptions
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account disabled")
    return user


def require_permission(permission_name: str):
    async def _require_permission(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.is_superuser or permission_name in user.permission_names:
            return user
        raise PermissionDeniedError(
            "You do not have permission to perform this action",
            details={"permission": permission_name},
        )

    return _require_permission
