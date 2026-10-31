from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import get_settings


def _new_jti() -> str:
    return uuid.uuid4().hex


def hash_password(password: str) -> str:
    settings = get_settings()
    pepper = settings.secret_key.get_secret_value()
    salt = hashlib.sha256(f"capitalos-password-salt:{pepper}".encode("utf-8")).hexdigest()[:16]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return f"pbkdf2${salt}${digest}"


def verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("pbkdf2$"):
        return False
    _, salt, expected = hashed_password.split("$", 2)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return hmac.compare_digest(candidate, expected)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    return hash_refresh_token(token) == token_hash


def create_access_token(subject: str, *, organization_id: str | None = None, permissions: list[str] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": _new_jti(),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=60)).timestamp()),
    }
    if organization_id is not None:
        payload["organization_id"] = organization_id
    if permissions:
        payload["permissions"] = permissions
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm="HS256")


def create_refresh_token(subject: str, *, organization_id: str | None = None) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": _new_jti(),
        "token_type": "refresh",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),
    }
    if organization_id is not None:
        payload["organization_id"] = organization_id
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=["HS256"])
    if payload.get("token_type") != "refresh":
        raise ValueError("Token type is not refresh")
    return payload
