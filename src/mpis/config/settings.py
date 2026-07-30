"""Application configuration dataclasses.

Google-style docstrings are used throughout. This module intentionally avoids
importing optional heavy dependencies so it can be imported safely in tests
without installing full runtime requirements.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class AppConfig:
    """Application configuration data.

    Args:
        project_root: Root path of the project.
        data_dir: Path to the data directory.
        cache_enabled: Whether caching is enabled.
    """

    project_root: Path
    data_dir: Path
    cache_enabled: bool = True

    @classmethod
    def default(cls) -> "AppConfig":
        """Return a reasonable default configuration based on project layout."""
        root = Path(__file__).resolve().parents[2]
        return cls(project_root=root, data_dir=root / "data", cache_enabled=True)

    def as_dict(self) -> Dict[str, Any]:
        """Serialize the configuration to a JSON-serializable dictionary."""
        return {
            "project_root": str(self.project_root),
            "data_dir": str(self.data_dir),
            "cache_enabled": self.cache_enabled,
        }
