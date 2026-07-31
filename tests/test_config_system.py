"""Tests for the configuration subsystem."""
from __future__ import annotations

from pathlib import Path

import pytest

from mpis.config import settings as global_settings
from mpis.config.settings import load_settings, Settings
from mpis.config.environment import Environment
from mpis.config.profiles import Profile


def test_default_loads_and_paths_exist() -> None:
    s = load_settings()
    assert isinstance(s, Settings)
    # project root should exist (repo root)
    assert s.project_root.exists()
    assert s.config_dir.exists()


def test_environment_switching() -> None:
    s_dev = load_settings(environment="development")
    assert s_dev.environment == Environment.DEVELOPMENT

    s_prod = load_settings(environment="production")
    assert s_prod.environment == Environment.PRODUCTION


def test_profile_switching() -> None:
    s_n = load_settings(profile="nifty")
    assert s_n.market == Profile.NIFTY

    s_b = load_settings(profile="banknifty")
    assert s_b.market == Profile.BANKNIFTY


def test_mode_override() -> None:
    s = load_settings(mode="live")
    assert s.mode == "live"


def test_global_settings_singleton_accessible() -> None:
    # ensure the package-level `settings` is accessible and has expected attrs
    assert hasattr(global_settings, "project_root")
    assert hasattr(global_settings, "data")


def test_invalid_config_raises() -> None:
    # create an invalid mapping missing required keys
    invalid = {"version": "0.1"}
    with pytest.raises(Exception):
        Settings.from_mapping(invalid)
