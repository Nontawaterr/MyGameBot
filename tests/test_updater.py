import pytest

from lib.updater import is_newer_version, normalize_version


@pytest.mark.parametrize(
    ("raw_version", "expected"),
    [
        ("1.0.0", (1,)),
        ("v1.2.3", (1, 2, 3)),
        (" 2.0-beta ", (2,)),
        ("", (0,)),
        (None, (0,)),
    ],
)
def test_normalize_version(raw_version, expected):
    assert normalize_version(raw_version) == expected


@pytest.mark.parametrize(
    ("latest", "current", "expected"),
    [
        ("1.0.1", "1.0.0", True),
        ("1.0.0", "1.0.0", False),
        ("v1.2.0", "1.1.9", True),
        ("1.0", "1.0.1", False),
    ],
)
def test_is_newer_version(latest, current, expected):
    assert is_newer_version(latest, current) is expected

