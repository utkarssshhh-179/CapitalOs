import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)


class LiveResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class ReadyResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, bool]


@router.get("/live", response_model=LiveResponse)
async def live(settings: Annotated[Settings, Depends(get_settings)]) -> LiveResponse:
    """Process is up. Used by container health checks."""
    return LiveResponse(version=settings.app_version)


@router.get("/ready", response_model=ReadyResponse)
async def ready(
    response: Response, session: Annotated[AsyncSession, Depends(get_session)]
) -> ReadyResponse:
    """Dependencies are reachable. Used by load balancers before routing traffic."""
    checks = {"database": await _check_database(session)}
    healthy = all(checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status="ok" if healthy else "degraded", checks=checks)


async def _check_database(session: AsyncSession) -> bool:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database readiness check failed")
        return False
    return True
