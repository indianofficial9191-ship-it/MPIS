"""Basic tests to ensure package imports work."""
from mpis import __version__  # type: ignore


def test_version_string() -> None:
    assert isinstance(__version__, str)
    assert __version__ != ""
