"""Append-only writer for audit events."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from snap_api.audit.models import AuditEvent


class AuditRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def record(
        self,
        *,
        action: str,
        actor_type: str = "system",
        actor_user_id: uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Stage an audit event on the current session (committed by the caller).

        `metadata` must be redacted — never include email, password, or tokens.
        """
        self.session.add(
            AuditEvent(
                action=action,
                actor_type=actor_type,
                actor_user_id=actor_user_id,
                target_type=target_type,
                target_id=target_id,
                event_metadata=metadata or {},
            )
        )
