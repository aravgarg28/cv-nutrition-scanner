"""Access-token creation and verification (JWT, HS256).

HS256 is appropriate for this first-party monolith (the same service signs and
verifies). EdDSA is the documented upgrade if third parties ever need to verify
tokens (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md). The refresh token is NOT
a JWT — it is an opaque value stored hashed in the sessions table.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from snap_api.core.config import get_settings

_ALGORITHM = "HS256"
_ISSUER = "snapnutrition"


@dataclass(frozen=True)
class AccessClaims:
    user_id: uuid.UUID
    role: str
    token_version: int


class InvalidAccessToken(Exception):
    """Raised when an access token is missing, malformed, expired, or wrong-issuer."""


def create_access_token(*, user_id: uuid.UUID, role: str, token_version: int) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "iss": _ISSUER,
        "sub": str(user_id),
        "role": role,
        "tv": token_version,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.jwt_access_ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_signing_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> AccessClaims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_signing_key,
            algorithms=[_ALGORITHM],
            issuer=_ISSUER,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
        return AccessClaims(
            user_id=uuid.UUID(payload["sub"]),
            role=payload["role"],
            token_version=int(payload["tv"]),
        )
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise InvalidAccessToken(str(exc)) from exc
