"""Tests for the configuration `Settings` API."""
from __future__ import annotations

from pathlib import Path

import pytest

from mpis.config.settings import Settings
from mpis.config.validators import ConfigurationError


def test_settings_from_mapping_and_path_resolution(tmp_path: Path) -> None:
    mapping = {
        "version": "0.1.0",
        "environment": "development",
        "profile": "nifty",
        "mode": "replay",
        "paths": {
            "data": "my_data",
            "logs": "my_logs",
            "reports": "my_reports",
            "cache": "my_cache",
            "configs": "configs",
        },
    }

    settings = Settings.from_mapping(mapping, project_root=tmp_path)
    assert settings.project_root == tmp_path
    assert settings.data == (tmp_path / "my_data").resolve()
    assert settings.logs == (tmp_path / "my_logs").resolve()
    assert settings.reports == (tmp_path / "my_reports").resolve()
    assert settings.cache == (tmp_path / "my_cache").resolve()
    assert settings.version == "0.1.0"
    assert settings.mode == "replay"


def test_settings_from_mapping_missing_keys_raises() -> None:
    incomplete = {"version": "0.1.0", "paths": {}}
    with pytest.raises(ConfigurationError):
        Settings.from_mapping(incomplete)


def test_settings_dataclass_is_frozen(tmp_path: Path) -> None:
    mapping = {
        "version": "0.1.0",
        "environment": "development",
        "profile": "nifty",
        "mode": "replay",
        "paths": {
            "data": "data",
            "logs": "logs",
            "reports": "reports",
            "cache": "cache",
            "configs": "configs",
        },
    }
    s = Settings.from_mapping(mapping, project_root=tmp_path)
    with pytest.raises(Exception):
        # dataclass is frozen; assignment should raise
        s.mode = "live"  # type: ignore
