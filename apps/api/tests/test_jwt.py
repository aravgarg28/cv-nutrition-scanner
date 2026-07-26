import uuid

import jwt
import pytest

from snap_api.core.config import get_settings
from snap_api.identity.jwt import (
    InvalidAccessToken,
    create_access_token,
    decode_access_token,
)


def test_create_and_decode_roundtrip() -> None:
    uid = uuid.uuid4()
    token = create_access_token(user_id=uid, role="user", token_version=3)
    claims = decode_access_token(token)
    assert claims.user_id == uid
    assert claims.role == "user"
    assert claims.token_version == 3


def test_tampered_token_rejected() -> None:
    token = create_access_token(user_id=uuid.uuid4(), role="user", token_version=0)
    with pytest.raises(InvalidAccessToken):
        decode_access_token(token + "x")


def test_wrong_key_rejected() -> None:
    token = create_access_token(user_id=uuid.uuid4(), role="user", token_version=0)
    forged = jwt.encode({"sub": "x"}, "some-other-key", algorithm="HS256")
    assert token != forged
    with pytest.raises(InvalidAccessToken):
        decode_access_token(forged)


def test_expired_token_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force an immediate expiry by setting the access TTL negative.
    settings = get_settings()
    monkeypatch.setattr(settings, "jwt_access_ttl_seconds", -1)
    token = create_access_token(user_id=uuid.uuid4(), role="user", token_version=0)
    with pytest.raises(InvalidAccessToken):
        decode_access_token(token)
