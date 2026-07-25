"""Identity ORM models (docs/architecture/DATA_MODEL.md §Identity)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from snap_api.core.db import Base, TimestampMixin
from snap_api.core.ids import uuid7

# Roles are a small closed set (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md).
USER_ROLES = ("user", "admin", "demo")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('user', 'admin', 'demo')", name="role_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    # Case-insensitive email (CITEXT) with a unique constraint. Emails are also
    # normalized to lowercase at the service boundary (defense in depth).
    email: Mapped[str] = mapped_column(CITEXT, unique=True)
    password_hash: Mapped[str]
    email_verified: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(default="user")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
