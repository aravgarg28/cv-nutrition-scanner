"""Identity use-cases: registration and email verification.

Registration is enumeration-safe: the response is identical whether or not the email
already exists (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md). Password policy
failures surface as PasswordPolicyError (mapped to 422 by the app).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from snap_api.core.config import get_settings
from snap_api.identity.email import EmailSender
from snap_api.identity.password_policy import validate_password
from snap_api.identity.passwords import hash_password
from snap_api.identity.repo import IdentityRepo
from snap_api.identity.tokens import generate_token, hash_token

EMAIL_VERIFICATION_TTL = timedelta(hours=24)


class InvalidTokenError(Exception):
    """Raised when a verification token is missing, expired, or already used."""


def _now() -> datetime:
    return datetime.now(UTC)


class IdentityService:
    def __init__(self, repo: IdentityRepo, email_sender: EmailSender) -> None:
        self.repo = repo
        self.email_sender = email_sender

    async def register(self, *, email: str, password: str) -> None:
        # Validate password before any DB work (raises PasswordPolicyError -> 422).
        validate_password(password)

        normalized = email.strip().lower()
        existing = await self.repo.get_user_by_email(normalized)
        if existing is not None:
            # Enumeration-safe: do not reveal that the account exists and do not create
            # a duplicate. A future task may send an "account already exists" email.
            return

        user = await self.repo.create_user(email=normalized, password_hash=hash_password(password))
        raw_token = generate_token()
        await self.repo.add_verification_token(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=_now() + EMAIL_VERIFICATION_TTL,
        )
        verify_url = f"{get_settings().public_base_url}/verify-email?token={raw_token}"
        self.email_sender.send_verification(normalized, verify_url)

    async def verify_email(self, *, token: str) -> None:
        record = await self.repo.get_verification_token(hash_token(token))
        if record is None or record.used_at is not None:
            raise InvalidTokenError
        if record.expires_at <= _now():
            raise InvalidTokenError

        user = await self.repo.get_user(record.user_id)
        if user is None:
            raise InvalidTokenError

        user.email_verified = True
        record.used_at = _now()
