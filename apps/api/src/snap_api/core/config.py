"""Application settings (12-factor, env-driven).

Secrets never live in code (docs/security/SECRET_MANAGEMENT.md); they arrive via the
environment. Local defaults target the Docker Compose stack so a fresh checkout runs
without hand-editing (docs/build/LOCAL_DEVELOPMENT.md).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "info"

    # Async SQLAlchemy URL. Compose default (host port may be overridden locally).
    database_url: str = "postgresql+asyncpg://snap:snap@localhost:5432/snap"

    # Public base URL used to build links in outgoing email.
    public_base_url: str = "http://localhost:8000"

    # Email delivery. 'console' prints links to the logs (local/test); real providers
    # are wired in later (docs/deployment/COST_MODEL.md).
    email_provider: str = "console"

    # JWT signing (HS256 for the first-party monolith; EdDSA is a documented upgrade
    # for multi-service verification). The default is insecure and MUST be overridden
    # outside local/test (docs/security/SECRET_MANAGEMENT.md).
    jwt_signing_key: str = "dev-insecure-do-not-use-in-production"
    jwt_access_ttl_seconds: int = 900  # 15 minutes
    jwt_refresh_ttl_seconds: int = 2_592_000  # 30 days


@lru_cache
def get_settings() -> Settings:
    return Settings()
