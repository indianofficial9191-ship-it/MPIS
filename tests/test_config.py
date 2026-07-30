"""Tests for configuration dataclass."""
from mpis.config.settings import AppConfig


def test_default_config() -> None:
    cfg = AppConfig.default()
    assert cfg.project_root.exists()
    assert cfg.data_dir.name == "data"
    assert isinstance(cfg.cache_enabled, bool)
