"""Audit ORM model (docs/architecture/DATA_MODEL.md §audit_event)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from snap_api.core.db import Base
from snap_api.core.ids import uuid7

ACTOR_TYPES = ("user", "system", "admin")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("actor_type IN ('user', 'system', 'admin')", name="actor_type_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    actor_type: Mapped[str]
    # No FK: audit must survive user deletion (accountability). Indexed for lookups.
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(index=True, default=None)
    action: Mapped[str] = mapped_column(index=True)
    target_type: Mapped[str | None] = mapped_column(default=None)
    target_id: Mapped[str | None] = mapped_column(default=None)
    # Redacted metadata only — never PII (docs/security/PRIVACY_MODEL.md). Column is
    # named "metadata" (the attribute avoids SQLAlchemy's reserved name).
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
