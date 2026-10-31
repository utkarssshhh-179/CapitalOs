from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import RefreshTokenRequest, TokenResponse, UserLogin, UserRegister, UserResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    service = AuthService(session)
    user = await service.register_user(payload)
    await session.commit()
    return await service.user_to_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    service = AuthService(session)
    token = await service.login_user(payload)
    await session.commit()
    return token


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    service = AuthService(session)
    token = await service.refresh_access_token(payload)
    await session.commit()
    return token


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    service = AuthService(session)
    return await service.user_to_response(current_user)
