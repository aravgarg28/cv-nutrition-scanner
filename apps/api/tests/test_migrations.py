"""Migration up/down + basic User persistence (integration; needs Postgres).

Opt-in via SNAP_INTEGRATION=1 with the compose stack running. Set DATABASE_URL (or
POSTGRES_HOST_PORT) to point at the database. The test upgrades to head, exercises the
users table, then downgrades to base — leaving the database clean.
"""

from __future__ import annotations

import asyncio
import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.integration

_ENABLED = os.environ.get("SNAP_INTEGRATION") == "1"
skip_unless_enabled = pytest.mark.skipif(
    not _ENABLED, reason="set SNAP_INTEGRATION=1 with the compose stack running"
)


def _database_url() -> str:
    if url := os.environ.get("DATABASE_URL"):
        return url
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    return f"postgresql+asyncpg://snap:snap@localhost:{port}/snap"


def _alembic_config() -> Config:
    os.environ["DATABASE_URL"] = _database_url()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return Config(os.path.join(root, "alembic.ini"))


async def _table_exists(url: str, name: str) -> bool:
    engine = create_async_engine(url, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT to_regclass(:n)"), {"n": f"public.{name}"})
            return result.scalar() is not None
    finally:
        await engine.dispose()


async def _insert_and_read_user(url: str) -> str:
    from snap_api.core.ids import uuid7
    from snap_api.identity.passwords import hash_password

    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            uid = uuid7()
            await conn.execute(
                text(
                    "INSERT INTO users (id, email, password_hash, email_verified, role) "
                    "VALUES (:id, :email, :ph, false, 'user')"
                ),
                {"id": uid, "email": "Person@Example.com", "ph": hash_password("x-strong-123")},
            )
        async with engine.connect() as conn:
            # CITEXT: case-insensitive match.
            row = await conn.execute(
                text("SELECT email FROM users WHERE email = :e"), {"e": "person@EXAMPLE.com"}
            )
            return row.scalar_one()
    finally:
        await engine.dispose()


@skip_unless_enabled
def test_migrations_up_down_and_user_persistence() -> None:
    url = _database_url()
    cfg = _alembic_config()

    command.upgrade(cfg, "head")
    assert asyncio.run(_table_exists(url, "users")) is True

    email = asyncio.run(_insert_and_read_user(url))
    assert email == "Person@Example.com"  # CITEXT preserves stored casing, matches insensitively

    command.downgrade(cfg, "base")
    assert asyncio.run(_table_exists(url, "users")) is False
