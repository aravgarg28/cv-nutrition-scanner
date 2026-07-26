"""Login / refresh / logout / me flows (integration; needs Postgres)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

STRONG = "tr0ub4dour-and-more"


async def _register(client: AsyncClient, email: str) -> None:
    resp = await client.post("/v1/auth/register", json={"email": email, "password": STRONG})
    assert resp.status_code == 202


async def _login(client: AsyncClient, email: str, password: str = STRONG):
    return await client.post("/v1/auth/login", json={"email": email, "password": password})


async def test_login_success_and_me(client: AsyncClient) -> None:
    await _register(client, "u@example.com")
    resp = await _login(client, "u@example.com")
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 900
    assert body["access_token"] and body["refresh_token"]

    me = await client.get(
        "/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "u@example.com"
    assert me.json()["role"] == "user"


async def test_me_requires_valid_token(client: AsyncClient) -> None:
    assert (await client.get("/v1/auth/me")).status_code == 401
    bad = await client.get("/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "unauthorized"


async def test_login_wrong_password_401(client: AsyncClient) -> None:
    await _register(client, "wp@example.com")
    resp = await _login(client, "wp@example.com", "totally-wrong-pass")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


async def test_login_unknown_email_401(client: AsyncClient) -> None:
    resp = await _login(client, "ghost@example.com")
    assert resp.status_code == 401


async def test_lockout_after_10_failures(client: AsyncClient) -> None:
    await _register(client, "lock@example.com")
    for _ in range(10):
        assert (await _login(client, "lock@example.com", "wrong-password-x")).status_code == 401
    # 11th attempt is locked out (423), even with the correct password.
    locked = await _login(client, "lock@example.com", STRONG)
    assert locked.status_code == 423
    assert locked.json()["error"]["code"] == "rate_limited"


async def test_refresh_rotates(client: AsyncClient) -> None:
    await _register(client, "r@example.com")
    r0 = (await _login(client, "r@example.com")).json()["refresh_token"]
    first = await client.post("/v1/auth/refresh", json={"refresh_token": r0})
    assert first.status_code == 200
    r1 = first.json()["refresh_token"]
    assert r1 != r0
    # The old token no longer works after rotation.
    assert (await client.post("/v1/auth/refresh", json={"refresh_token": r0})).status_code == 401


async def test_refresh_reuse_revokes_family(client: AsyncClient) -> None:
    await _register(client, "reuse@example.com")
    r0 = (await _login(client, "reuse@example.com")).json()["refresh_token"]
    r1 = (await client.post("/v1/auth/refresh", json={"refresh_token": r0})).json()["refresh_token"]
    # Replay the already-rotated r0: reuse detected -> whole family revoked.
    replay = await client.post("/v1/auth/refresh", json={"refresh_token": r0})
    assert replay.status_code == 401
    # r1 was valid but is now revoked because the family was killed.
    assert (await client.post("/v1/auth/refresh", json={"refresh_token": r1})).status_code == 401


async def test_logout_revokes_family(client: AsyncClient) -> None:
    await _register(client, "out@example.com")
    r0 = (await _login(client, "out@example.com")).json()["refresh_token"]
    assert (await client.post("/v1/auth/logout", json={"refresh_token": r0})).status_code == 200
    assert (await client.post("/v1/auth/refresh", json={"refresh_token": r0})).status_code == 401
