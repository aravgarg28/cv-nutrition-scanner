"""Password strength policy (docs/security/AUTHENTICATION_AND_AUTHORIZATION.md).

Rules: length 10-128; reject known-common passwords via a bundled list; reject
trivially weak shapes (single repeated character, obvious sequences). Raises
`PasswordPolicyError` with a stable reason code so the signup endpoint (T-007) can
return a 422 `validation_error`.

Breach list: `data/common_passwords.txt` ships as a *starter* list. Replacing it with
the full top-100k list (offline, free) is a follow-up data-asset task; the loader
already handles any size.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

MIN_LENGTH = 10
MAX_LENGTH = 128

_COMMON_PASSWORDS_FILE = Path(__file__).parent / "data" / "common_passwords.txt"


class PasswordPolicyError(ValueError):
    """Raised when a password fails policy. `reason` is a stable machine code."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message


@lru_cache
def _common_passwords() -> frozenset[str]:
    if not _COMMON_PASSWORDS_FILE.exists():
        return frozenset()
    lines = _COMMON_PASSWORDS_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip().lower() for line in lines if line.strip())


def _is_single_char(password: str) -> bool:
    return len(set(password)) == 1


def _is_sequential(password: str) -> bool:
    lowered = password.lower()
    sequences = ("abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiop")
    return any(lowered in seq or lowered[::-1] in seq for seq in sequences)


def validate_password(password: str) -> None:
    """Validate a password, raising PasswordPolicyError on the first failure."""
    if len(password) < MIN_LENGTH:
        raise PasswordPolicyError(
            "too_short", f"Password must be at least {MIN_LENGTH} characters."
        )
    if len(password) > MAX_LENGTH:
        raise PasswordPolicyError("too_long", f"Password must be at most {MAX_LENGTH} characters.")
    if _is_single_char(password):
        raise PasswordPolicyError("too_weak", "Password is too simple.")
    if _is_sequential(password):
        raise PasswordPolicyError("too_weak", "Password is too simple.")
    if password.lower() in _common_passwords():
        raise PasswordPolicyError("too_common", "This password is too common.")
