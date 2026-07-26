"""Data access for the identity module (users + verification tokens)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from snap_api.identity.models import (
    EmailVerificationToken,
    PasswordResetToken,
    Session,
    User,
)


class IdentityRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, *, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()
        return user

    async def add_verification_token(
        self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> EmailVerificationToken:
        token = EmailVerificationToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_verification_token(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    # --- sessions (refresh-token families) ---

    async def create_session(
        self,
        *,
        user_id: uuid.UUID,
        family_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        device_label: str | None,
    ) -> Session:
        record = Session(
            user_id=user_id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
            device_label=device_label,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_session_by_hash(self, token_hash: str) -> Session | None:
        result = await self.session.execute(select(Session).where(Session.token_hash == token_hash))
        return result.scalar_one_or_none()

    async def revoke_family(self, family_id: uuid.UUID, *, at: datetime) -> None:
        """Revoke every still-active token in a rotation family."""
        await self.session.execute(
            update(Session)
            .where(Session.family_id == family_id, Session.revoked_at.is_(None))
            .values(revoked_at=at)
        )

    async def revoke_all_sessions(self, user_id: uuid.UUID, *, at: datetime) -> None:
        """Revoke every active refresh token for a user (all families)."""
        await self.session.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .values(revoked_at=at)
        )

    # --- password reset tokens ---

    async def add_password_reset_token(
        self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_password_reset_token(self, token_hash: str) -> PasswordResetToken | None:
        result = await self.session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()
