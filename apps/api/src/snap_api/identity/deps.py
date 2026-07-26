"""Authentication dependency: resolve the current user from a Bearer access token."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from snap_api.core.db import get_session
from snap_api.core.errors import ApiError
from snap_api.identity.jwt import InvalidAccessToken, decode_access_token
from snap_api.identity.models import User
from snap_api.identity.repo import IdentityRepo

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise ApiError.unauthorized("Missing bearer token.")
    try:
        claims = decode_access_token(credentials.credentials)
    except InvalidAccessToken as exc:
        raise ApiError.unauthorized("Invalid or expired token.") from exc

    user = await IdentityRepo(session).get_user(claims.user_id)
    if user is None or user.token_version != claims.token_version:
        # Unknown user, or the token was invalidated by a token_version bump.
        raise ApiError.unauthorized("Invalid or expired token.")
    return user
