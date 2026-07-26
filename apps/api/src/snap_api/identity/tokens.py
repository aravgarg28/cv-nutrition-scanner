"""Opaque token generation and hashing.

Raw tokens are shown to the user once (in an email link); only their SHA-256 hash is
stored, so a database leak does not expose usable tokens.
"""

from __future__ import annotations

import hashlib
import secrets

_TOKEN_BYTES = 32


def generate_token() -> str:
    """Return a URL-safe random token (the raw value to send to the user)."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def hash_token(raw: str) -> str:
    """Deterministic hash for storage/lookup."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
