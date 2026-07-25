"""Password hashing (argon2id).

Parameters follow docs/security/AUTHENTICATION_AND_AUTHORIZATION.md; they are tunable
to the host. `needs_rehash` lets us transparently upgrade parameters over time.
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# memory 64 MiB, time cost 3, parallelism 4 (argon2id is the argon2-cffi default type).
_hasher = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)
