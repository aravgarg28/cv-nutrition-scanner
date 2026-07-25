import uuid

from snap_api.core.ids import uuid7


def test_uuid7_version_and_variant() -> None:
    u = uuid7()
    assert isinstance(u, uuid.UUID)
    assert u.version == 7
    assert u.variant == uuid.RFC_4122


def test_uuid7_values_are_unique() -> None:
    assert len({uuid7() for _ in range(1000)}) == 1000


def test_uuid7_is_time_ordered() -> None:
    # Successive UUIDs should be non-decreasing over time (ms-resolution timestamp
    # prefix). Compare batches separated by a millisecond boundary.
    import time

    a = uuid7()
    time.sleep(0.002)
    b = uuid7()
    assert a < b
