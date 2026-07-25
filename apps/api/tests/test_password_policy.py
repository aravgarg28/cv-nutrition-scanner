import pytest

from snap_api.identity.password_policy import (
    MAX_LENGTH,
    PasswordPolicyError,
    validate_password,
)


def test_accepts_a_strong_password() -> None:
    validate_password("tr0ub4dour-and-more")  # no raise


def test_rejects_too_short() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("short1")
    assert exc.value.reason == "too_short"


def test_rejects_too_long() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("a" * (MAX_LENGTH + 1))
    assert exc.value.reason == "too_long"


def test_rejects_common_password() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("password123")
    assert exc.value.reason == "too_common"


def test_rejects_common_password_case_insensitively() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("PassWord123")
    assert exc.value.reason == "too_common"


def test_rejects_single_char_repeat() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("aaaaaaaaaaaa")
    assert exc.value.reason == "too_weak"


def test_rejects_sequential() -> None:
    with pytest.raises(PasswordPolicyError) as exc:
        validate_password("abcdefghij")
    assert exc.value.reason == "too_weak"
