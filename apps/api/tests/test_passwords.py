from snap_api.identity.passwords import hash_password, needs_rehash, verify_password


def test_hash_is_not_plaintext_and_is_argon2id() -> None:
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"
    assert h.startswith("$argon2id$")


def test_verify_roundtrip() -> None:
    h = hash_password("correct horse battery staple")
    assert verify_password(h, "correct horse battery staple") is True
    assert verify_password(h, "wrong password entirely") is False


def test_verify_handles_garbage_hash() -> None:
    assert verify_password("not-a-real-hash", "whatever") is False


def test_hashes_are_salted_and_unique() -> None:
    assert hash_password("same-password-123") != hash_password("same-password-123")


def test_needs_rehash_returns_bool() -> None:
    assert needs_rehash(hash_password("some-password-123")) is False
