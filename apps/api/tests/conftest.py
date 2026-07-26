"""Fixtures for DB-backed API tests (integration; need Postgres).

Opt-in via SNAP_INTEGRATION=1. The `client` fixture wires the app against a test
database and a capturing email sender so tests can read the verification token.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

_ENABLED = os.environ.get("SNAP_INTEGRATION") == "1"


def _database_url() -> str:
    if url := os.environ.get("DATABASE_URL"):
        return url
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    return f"postgresql+asyncpg://snap:snap@localhost:{port}/snap"


def _alembic_config() -> Config:
    os.environ["DATABASE_URL"] = _database_url()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return Config(os.path.join(root, "alembic.ini"))


@dataclass
class CapturingEmailSender:
    sent: list[tuple[str, str]] = field(default_factory=list)

    def send_verification(self, email: str, verify_url: str) -> None:
        self.sent.append((email, verify_url))

    def last_token(self) -> str:
        from urllib.parse import parse_qs, urlparse

        _, url = self.sent[-1]
        return parse_qs(urlparse(url).query)["token"][0]


@pytest.fixture(scope="session")
def _migrated_db() -> Iterator[None]:
    if not _ENABLED:
        pytest.skip("set SNAP_INTEGRATION=1 with Postgres running")
    cfg = _alembic_config()
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest_asyncio.fixture
async def _clean_tables(_migrated_db: None) -> AsyncIterator[None]:
    engine = create_async_engine(_database_url())
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "TRUNCATE audit_events, password_reset_tokens, sessions, "
                    "email_verification_tokens, users RESTART IDENTITY CASCADE"
                )
            )
        yield
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def email_sender() -> CapturingEmailSender:
    return CapturingEmailSender()


@pytest_asyncio.fixture
async def client(
    _clean_tables: None, email_sender: CapturingEmailSender
) -> AsyncIterator[AsyncClient]:
    from snap_api.core.db import get_session
    from snap_api.identity.email import get_email_sender
    from snap_api.main import app

    engine = create_async_engine(_database_url())
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_session() -> AsyncIterator[object]:
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
