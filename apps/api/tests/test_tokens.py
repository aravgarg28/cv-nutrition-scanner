from snap_api.identity.tokens import generate_token, hash_token


def test_hash_is_deterministic() -> None:
    assert hash_token("abc") == hash_token("abc")


def test_hash_is_sha256_hex() -> None:
    h = hash_token("abc")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_generated_tokens_are_unique() -> None:
    assert len({generate_token() for _ in range(1000)}) == 1000


def test_different_inputs_hash_differently() -> None:
    assert hash_token(generate_token()) != hash_token(generate_token())
