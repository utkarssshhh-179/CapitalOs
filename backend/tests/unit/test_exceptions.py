from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import ConflictError, register_exception_handlers


async def test_app_error_maps_to_envelope():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise ConflictError("duplicate PAN", details={"field": "pan"})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/boom")
    assert r.status_code == 409
    body = r.json()["error"]
    assert body["code"] == "conflict" and body["details"] == {"field": "pan"}
