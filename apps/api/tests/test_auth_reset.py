"""Password-reset flow + audit events (integration; needs Postgres)."""

from __future__ import annotations

import os

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine

from snap_api.audit.models import AuditEvent

pytestmark = pytest.mark.integration

STRONG = "tr0ub4dour-and-more"
NEWPASS = "s0mething-Else-entirely"


def _db_url() -> str:
    if url := os.environ.get("DATABASE_URL"):
        return url
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    return f"postgresql+asyncpg://snap:snap@localhost:{port}/snap"


async def _audit_actions() -> list[str]:
    engine = create_async_engine(_db_url())
    try:
        async with engine.connect() as conn:
            rows = await conn.execute(select(AuditEvent.action))
            return [r[0] for r in rows]
    finally:
        await engine.dispose()


async def _count(action: str) -> int:
    engine = create_async_engine(_db_url())
    try:
        async with engine.connect() as conn:
            return (
                await conn.execute(
                    select(func.count()).select_from(AuditEvent).where(AuditEvent.action == action)
                )
            ).scalar_one()
    finally:
        await engine.dispose()


async def _register(client: AsyncClient, email: str) -> None:
    assert (
        await client.post("/v1/auth/register", json={"email": email, "password": STRONG})
    ).status_code == 202


async def test_reset_changes_password_and_revokes_sessions(
    client: AsyncClient, email_sender
) -> None:
    await _register(client, "reset@example.com")
    # An active login (refresh token) that must be revoked by the reset.
    old_refresh = (
        await client.post("/v1/auth/login", json={"email": "reset@example.com", "password": STRONG})
    ).json()["refresh_token"]

    # Request reset; capture the emailed token.
    assert (
        await client.post("/v1/auth/password-reset", json={"email": "Reset@example.com"})
    ).status_code == 202
    reset_token = email_sender.last_token()

    # Confirm with a new password.
    confirm = await client.post(
        "/v1/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": NEWPASS},
    )
    assert confirm.status_code == 200

    # Old password no longer works; new one does.
    assert (
        await client.post("/v1/auth/login", json={"email": "reset@example.com", "password": STRONG})
    ).status_code == 401
    assert (
        await client.post(
            "/v1/auth/login", json={"email": "reset@example.com", "password": NEWPASS}
        )
    ).status_code == 200
    # Pre-reset refresh token was revoked.
    assert (
        await client.post("/v1/auth/refresh", json={"refresh_token": old_refresh})
    ).status_code == 401


async def test_reset_request_is_enumeration_safe(client: AsyncClient) -> None:
    resp = await client.post("/v1/auth/password-reset", json={"email": "nobody@example.com"})
    assert resp.status_code == 202
    assert resp.json() == {"status": "reset_email_sent"}


async def test_reset_confirm_weak_password_rejected(client: AsyncClient, email_sender) -> None:
    await _register(client, "weakreset@example.com")
    await client.post("/v1/auth/password-reset", json={"email": "weakreset@example.com"})
    token = email_sender.last_token()
    resp = await client.post(
        "/v1/auth/password-reset/confirm", json={"token": token, "new_password": "password123"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


async def test_reset_token_single_use(client: AsyncClient, email_sender) -> None:
    await _register(client, "single@example.com")
    await client.post("/v1/auth/password-reset", json={"email": "single@example.com"})
    token = email_sender.last_token()
    assert (
        await client.post(
            "/v1/auth/password-reset/confirm", json={"token": token, "new_password": NEWPASS}
        )
    ).status_code == 200
    second = await client.post(
        "/v1/auth/password-reset/confirm", json={"token": token, "new_password": "an0ther-Pass-x"}
    )
    assert second.status_code == 422


async def test_audit_events_recorded(client: AsyncClient) -> None:
    await _register(client, "audit@example.com")
    await client.post("/v1/auth/login", json={"email": "audit@example.com", "password": STRONG})
    await client.post("/v1/auth/login", json={"email": "audit@example.com", "password": "wrong-x"})
    actions = await _audit_actions()
    assert "user.registered" in actions
    assert "auth.login_succeeded" in actions
    assert "auth.login_failed" in actions


async def test_lockout_emits_account_locked_audit(client: AsyncClient) -> None:
    await _register(client, "lockaudit@example.com")
    for _ in range(10):
        await client.post(
            "/v1/auth/login", json={"email": "lockaudit@example.com", "password": "nope-x"}
        )
    assert await _count("auth.account_locked") == 1
