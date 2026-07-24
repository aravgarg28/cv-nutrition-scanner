import snap_shared_schemas


def test_package_importable() -> None:
    assert snap_shared_schemas.__version__ == "0.0.0"
