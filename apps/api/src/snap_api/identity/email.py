"""Email delivery.

An `EmailSender` protocol keeps the provider swappable. The console sender prints the
link to logs for local/test; real transactional providers are wired later
(docs/deployment/COST_MODEL.md, docs/security/SECRET_MANAGEMENT.md).
"""

from __future__ import annotations

import logging
from typing import Protocol

from snap_api.core.config import get_settings

logger = logging.getLogger("snap_api.email")


class EmailSender(Protocol):
    def send_verification(self, email: str, verify_url: str) -> None: ...


class ConsoleEmailSender:
    """Prints the verification link instead of sending it (local/test)."""

    def send_verification(self, email: str, verify_url: str) -> None:
        logger.info("email.verification to=%s url=%s", email, verify_url)


def get_email_sender() -> EmailSender:
    """FastAPI dependency: select the configured email sender."""
    provider = get_settings().email_provider
    if provider == "console":
        return ConsoleEmailSender()
    # Real providers (e.g. Brevo/Resend) are added with their own config in a later
    # task; fail closed rather than silently dropping mail.
    raise RuntimeError(f"Unsupported EMAIL_PROVIDER: {provider!r}")
