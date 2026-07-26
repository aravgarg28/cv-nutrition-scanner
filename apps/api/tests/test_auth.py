"""Register + verify-email flow (integration; needs Postgres)."""

from __future__ import annotations

import os

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine

from snap_api.identity.models import User

pytestmark = pytest.mark.integration


def _db_url() -> str:
    if url := os.environ.get("DATABASE_URL"):
        return url
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    return f"postgresql+asyncpg://snap:snap@localhost:{port}/snap"


async def _user_count() -> int:
    engine = create_async_engine(_db_url())
    try:
        async with engine.connect() as conn:
            return (await conn.execute(select(func.count()).select_from(User))).scalar_one()
    finally:
        await engine.dispose()


async def _email_verified(email: str) -> bool | None:
    """Return the user's email_verified flag, or None if no such user."""
    engine = create_async_engine(_db_url())
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(select(User.email_verified).where(User.email == email))
            ).first()
            return None if row is None else bool(row[0])
    finally:
        await engine.dispose()


STRONG = "tr0ub4dour-and-more"


async def test_register_creates_unverified_user_and_sends_email(client, email_sender) -> None:
    resp = await client.post("/v1/auth/register", json={"email": "Foo@Bar.com", "password": STRONG})
    assert resp.status_code == 202
    assert resp.json() == {"status": "verification_sent"}
    # Email normalized to lowercase, unverified, one email sent.
    assert await _user_count() == 1
    assert await _email_verified("foo@bar.com") is False
    assert len(email_sender.sent) == 1
    assert email_sender.sent[0][0] == "foo@bar.com"


async def test_verify_email_marks_verified(client, email_sender) -> None:
    await client.post("/v1/auth/register", json={"email": "v@example.com", "password": STRONG})
    token = email_sender.last_token()
    resp = await client.post("/v1/auth/verify-email", json={"token": token})
    assert resp.status_code == 200
    assert resp.json() == {"status": "verified"}
    assert await _email_verified("v@example.com") is True


async def test_verify_token_is_single_use(client, email_sender) -> None:
    await client.post("/v1/auth/register", json={"email": "once@example.com", "password": STRONG})
    token = email_sender.last_token()
    assert (await client.post("/v1/auth/verify-email", json={"token": token})).status_code == 200
    second = await client.post("/v1/auth/verify-email", json={"token": token})
    assert second.status_code == 422
    assert second.json()["error"]["code"] == "validation_error"


async def test_duplicate_registration_is_enumeration_safe(client: AsyncClient) -> None:
    body = {"email": "dup@example.com", "password": STRONG}
    first = await client.post("/v1/auth/register", json=body)
    second = await client.post("/v1/auth/register", json=body)
    # Identical responses, and no duplicate user created.
    assert first.status_code == second.status_code == 202
    assert first.json() == second.json()
    assert await _user_count() == 1


async def test_weak_password_rejected(client: AsyncClient) -> None:
    resp = await client.post(
        "/v1/auth/register", json={"email": "weak@example.com", "password": "password123"}
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["request_id"]  # request id populated
    assert await _user_count() == 0


async def test_invalid_email_rejected(client: AsyncClient) -> None:
    resp = await client.post(
        "/v1/auth/register", json={"email": "not-an-email", "password": STRONG}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


async def test_verify_unknown_token_rejected(client: AsyncClient) -> None:
    resp = await client.post("/v1/auth/verify-email", json={"token": "nope"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"
