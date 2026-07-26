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


@lru_cache
def get_settings() -> Settings:
    return Settings()
