import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("CAPITALOS_ENVIRONMENT", "test")
os.environ.setdefault("CAPITALOS_LOG_JSON", "false")

from app.db.session import get_session  # noqa: E402
from app.main import create_app  # noqa: E402


class FakeSession:
    """Stands in for AsyncSession in API tests that don't need a database."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    async def execute(self, *_: object, **__: object) -> None:
        if self.fail:
            raise ConnectionError("db down")


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async def _ok() -> AsyncIterator[FakeSession]:
        yield FakeSession()

    app.dependency_overrides[get_session] = _ok
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
