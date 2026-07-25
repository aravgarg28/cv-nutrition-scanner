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


@lru_cache
def get_settings() -> Settings:
    return Settings()
