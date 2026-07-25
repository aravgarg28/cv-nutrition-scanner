"""Smoke test for the local Docker Compose stack (T-003).

Verifies the compose services are reachable — no application DB code yet (that lands
in T-006+), so this uses only stdlib to avoid premature dependencies. Skipped unless
SNAP_INTEGRATION=1 so the default `uv run pytest` stays green without Docker.

Run against a running stack:
    docker compose -f docker/compose.yaml up -d
    SNAP_INTEGRATION=1 uv run pytest -m integration
"""

import os
import socket
import urllib.request

import pytest

pytestmark = pytest.mark.integration

_ENABLED = os.environ.get("SNAP_INTEGRATION") == "1"
skip_unless_enabled = pytest.mark.skipif(
    not _ENABLED, reason="set SNAP_INTEGRATION=1 with the compose stack running"
)


def _tcp_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (localhost)
            return resp.status == 200
    except Exception:
        return False


_PG_PORT = int(os.environ.get("POSTGRES_HOST_PORT", "5432"))
_MINIO_PORT = int(os.environ.get("MINIO_API_PORT", "9000"))
_API_PORT = int(os.environ.get("API_HOST_PORT", "8000"))


@skip_unless_enabled
def test_postgres_port_open() -> None:
    assert _tcp_open("127.0.0.1", _PG_PORT), f"Postgres not reachable on :{_PG_PORT}"


@skip_unless_enabled
def test_minio_healthy() -> None:
    assert _http_ok(f"http://127.0.0.1:{_MINIO_PORT}/minio/health/live"), (
        f"MinIO not healthy on :{_MINIO_PORT}"
    )


@skip_unless_enabled
def test_api_healthz() -> None:
    url = f"http://127.0.0.1:{_API_PORT}/healthz"
    assert _http_ok(url), f"API /healthz not reachable on :{_API_PORT}"
