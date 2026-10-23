from app.db.session import get_session
from tests.conftest import FakeSession


async def test_live_returns_ok_and_request_id(client):
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.headers["x-request-id"]
    assert r.headers["x-content-type-options"] == "nosniff"


async def test_request_id_is_propagated(client):
    r = await client.get("/api/v1/health/live", headers={"x-request-id": "abc123"})
    assert r.headers["x-request-id"] == "abc123"


async def test_ready_ok_when_database_up(client):
    r = await client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "checks": {"database": True}}


async def test_ready_503_when_database_down(app, client):
    async def _down():
        yield FakeSession(fail=True)

    app.dependency_overrides[get_session] = _down
    r = await client.get("/api/v1/health/ready")
    assert r.status_code == 503
    assert r.json()["checks"]["database"] is False


async def test_unknown_route_uses_error_envelope(client):
    r = await client.get("/api/v1/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "http_error"
