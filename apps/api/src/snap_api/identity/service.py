"""Identity use-cases: registration and email verification.

Registration is enumeration-safe: the response is identical whether or not the email
already exists (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md). Password policy
failures surface as PasswordPolicyError (mapped to 422 by the app).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from snap_api.audit import actions
from snap_api.audit.repo import AuditRepo
from snap_api.core.config import get_settings
from snap_api.core.errors import ApiError
from snap_api.core.ids import uuid7
from snap_api.identity.email import EmailSender
from snap_api.identity.jwt import create_access_token
from snap_api.identity.models import User
from snap_api.identity.password_policy import validate_password
from snap_api.identity.passwords import hash_password, verify_password
from snap_api.identity.repo import IdentityRepo
from snap_api.identity.tokens import generate_token, hash_token

EMAIL_VERIFICATION_TTL = timedelta(hours=24)
PASSWORD_RESET_TTL = timedelta(hours=1)

# Lockout policy (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md).
LOCKOUT_WINDOW = timedelta(minutes=15)
LOCK_DURATION = timedelta(minutes=15)
MAX_FAILED_LOGINS = 10

# Precomputed hash used to equalize timing when the email is unknown.
_DUMMY_PASSWORD_HASH = hash_password("timing-equalizer-not-a-real-password")


class InvalidTokenError(Exception):
    """Raised when a verification token is missing, expired, or already used."""


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int


def _now() -> datetime:
    return datetime.now(UTC)


class IdentityService:
    def __init__(self, repo: IdentityRepo, email_sender: EmailSender, audit: AuditRepo) -> None:
        self.repo = repo
        self.email_sender = email_sender
        self.audit = audit

    def _audit_user(self, action: str, user: User, **metadata) -> None:
        self.audit.record(
            action=action,
            actor_type="user",
            actor_user_id=user.id,
            target_type="user",
            target_id=str(user.id),
            metadata=metadata or None,
        )

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
        self._audit_user(actions.USER_REGISTERED, user)

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
        self._audit_user(actions.EMAIL_VERIFIED, user)

    # --- login / refresh / logout ---

    async def _issue_tokens(
        self, user: User, *, family_id, device_label: str | None
    ) -> IssuedTokens:
        settings = get_settings()
        access = create_access_token(
            user_id=user.id, role=user.role, token_version=user.token_version
        )
        raw_refresh = generate_token()
        await self.repo.create_session(
            user_id=user.id,
            family_id=family_id,
            token_hash=hash_token(raw_refresh),
            expires_at=_now() + timedelta(seconds=settings.jwt_refresh_ttl_seconds),
            device_label=device_label,
        )
        return IssuedTokens(
            access_token=access,
            refresh_token=raw_refresh,
            expires_in=settings.jwt_access_ttl_seconds,
        )

    @staticmethod
    def _record_failed_login(user: User, now: datetime) -> None:
        if user.last_failed_at is not None and now - user.last_failed_at > LOCKOUT_WINDOW:
            user.failed_login_count = 0
        user.failed_login_count += 1
        user.last_failed_at = now
        if user.failed_login_count >= MAX_FAILED_LOGINS:
            user.locked_until = now + LOCK_DURATION
            user.failed_login_count = 0

    async def login(
        self, *, email: str, password: str, device_label: str | None = None
    ) -> IssuedTokens:
        normalized = email.strip().lower()
        now = _now()
        user = await self.repo.get_user_by_email(normalized)

        if user is None:
            # Equalize timing so a missing account is indistinguishable from a wrong
            # password, then fail with the same generic message.
            verify_password(_DUMMY_PASSWORD_HASH, password)
            raise ApiError.unauthorized("Email or password is incorrect.")

        if user.locked_until is not None and user.locked_until > now:
            self._audit_user(actions.LOGIN_FAILED, user, reason="locked")
            raise ApiError.locked("Too many failed attempts. Try again later.")

        if not verify_password(user.password_hash, password):
            was_unlocked = user.locked_until is None
            self._record_failed_login(user, now)
            self._audit_user(actions.LOGIN_FAILED, user, reason="bad_password")
            if was_unlocked and user.locked_until is not None:
                self._audit_user(actions.ACCOUNT_LOCKED, user)
            raise ApiError.unauthorized("Email or password is incorrect.")

        # Success: clear failure bookkeeping and issue a fresh token family.
        user.failed_login_count = 0
        user.locked_until = None
        user.last_failed_at = None
        tokens = await self._issue_tokens(user, family_id=uuid7(), device_label=device_label)
        self._audit_user(actions.LOGIN_SUCCEEDED, user)
        return tokens

    async def refresh(self, *, refresh_token: str) -> IssuedTokens:
        now = _now()
        record = await self.repo.get_session_by_hash(hash_token(refresh_token))
        if record is None:
            raise ApiError.unauthorized("Invalid refresh token.")

        if record.revoked_at is not None:
            # A revoked/rotated token was replayed: treat as theft, kill the family.
            await self.repo.revoke_family(record.family_id, at=now)
            raise ApiError.unauthorized("Invalid refresh token.")

        if record.expires_at <= now:
            await self.repo.revoke_family(record.family_id, at=now)
            raise ApiError.unauthorized("Invalid refresh token.")

        user = await self.repo.get_user(record.user_id)
        if user is None:
            raise ApiError.unauthorized("Invalid refresh token.")

        # Rotate: revoke the presented token and issue a successor in the same family.
        record.revoked_at = now
        return await self._issue_tokens(
            user, family_id=record.family_id, device_label=record.device_label
        )

    async def logout(self, *, refresh_token: str) -> None:
        record = await self.repo.get_session_by_hash(hash_token(refresh_token))
        if record is not None:
            await self.repo.revoke_family(record.family_id, at=_now())
            self.audit.record(
                action=actions.LOGGED_OUT,
                actor_type="user",
                actor_user_id=record.user_id,
                target_type="user",
                target_id=str(record.user_id),
            )

    # --- password reset ---

    async def request_password_reset(self, *, email: str) -> None:
        normalized = email.strip().lower()
        user = await self.repo.get_user_by_email(normalized)
        if user is None:
            # Enumeration-safe: identical response whether or not the account exists.
            return
        raw_token = generate_token()
        await self.repo.add_password_reset_token(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=_now() + PASSWORD_RESET_TTL,
        )
        reset_url = f"{get_settings().public_base_url}/reset-password?token={raw_token}"
        self.email_sender.send_verification(normalized, reset_url)
        self._audit_user(actions.PASSWORD_RESET_REQUESTED, user)

    async def confirm_password_reset(self, *, token: str, new_password: str) -> None:
        # Validate the new password first (raises PasswordPolicyError -> 422).
        validate_password(new_password)
        now = _now()
        record = await self.repo.get_password_reset_token(hash_token(token))
        if record is None or record.used_at is not None or record.expires_at <= now:
            raise ApiError.validation("Invalid or expired reset token.")
        user = await self.repo.get_user(record.user_id)
        if user is None:
            raise ApiError.validation("Invalid or expired reset token.")

        user.password_hash = hash_password(new_password)
        # Invalidate all outstanding access tokens (token_version) and refresh tokens.
        user.token_version += 1
        user.failed_login_count = 0
        user.locked_until = None
        await self.repo.revoke_all_sessions(user.id, at=now)
        record.used_at = now
        self._audit_user(actions.PASSWORD_RESET_COMPLETED, user)
