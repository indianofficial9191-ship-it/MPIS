"""Settings model and loader for MPIS.

This module provides a `Settings` dataclass that is constructed by loading
YAML configuration files and validated. Use `load_settings` to create an
instance. The package `__init__` exposes a singleton `settings` instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .constants import PROJECT_CONFIG_DIR
from .environment import Environment
from .loader import load_configs
from .profiles import Profile
from .validators import ConfigurationError, validate_keys


@dataclass(frozen=True)
class Settings:
    """Application settings.

    Attributes:
        project_root: Root path of the project.
        data: Path to data folder.
        logs: Path to logs folder.
        reports: Path to reports folder.
        cache: Path to cache folder.
        config_dir: Path to configuration folder.
        version: Application version string.
        environment: Runtime environment.
        market: Current market profile.
        mode: Trading mode (replay/live/paper).
        raw: Raw merged configuration mapping.
    """

    project_root: Path
    data: Path
    logs: Path
    reports: Path
    cache: Path
    config_dir: Path
    version: str
    environment: Environment
    market: Profile
    mode: str
    raw: Dict[str, Any]

    @classmethod
    def from_mapping(
        cls, mapping: Dict[str, Any], project_root: Path | None = None
    ) -> "Settings":
        """Create `Settings` from a merged configuration mapping.

        Args:
            mapping: Merged configuration dict.
            project_root: Optional explicit project root path.

        Raises:
            ConfigurationError: For missing or invalid values.
        """
        required = {
            "version": str,
            "paths": dict,
            "environment": str,
            "profile": str,
            "mode": str,
        }
        validate_keys(mapping, required)

        pr = Path(project_root) if project_root else Path(__file__).resolve().parents[3]

        paths = mapping["paths"]
        req_paths = {
            "data": str,
            "logs": str,
            "reports": str,
            "cache": str,
            "configs": str,
        }
        validate_keys(paths, req_paths)

        config_dir = pr / paths["configs"]

        try:
            env = Environment.from_str(mapping["environment"])
        except ValueError as exc:
            raise ConfigurationError(str(exc))

        try:
            prof = Profile.from_str(mapping["profile"])
        except ValueError as exc:
            raise ConfigurationError(str(exc))

        return cls(
            project_root=pr,
            data=(pr / paths["data"]).resolve(),
            logs=(pr / paths["logs"]).resolve(),
            reports=(pr / paths["reports"]).resolve(),
            cache=(pr / paths["cache"]).resolve(),
            config_dir=config_dir.resolve(),
            version=str(mapping["version"]),
            environment=env,
            market=prof,
            mode=str(mapping["mode"]),
            raw=mapping,
        )


def load_settings(
    environment: str | None = None,
    profile: str | None = None,
    mode: str | None = None,
    config_dir: Path | None = None,
    project_root: Path | None = None,
) -> Settings:
    """Load settings from YAML files.

    Loading strategy:
    - Start from `configs/default.yaml`.
    - Overlay environment-specific YAML if present (e.g., `development.yaml`).
    - Overlay mode/profile-specific YAML files if present.

    Args:
        environment: Optional environment name to load.
        profile: Optional market profile name.
        mode: Optional trading mode.
        config_dir: Optional config directory path.
        project_root: Optional project root for path resolution.

    Returns:
        A validated `Settings` instance.
    """
    cfg_dir = config_dir or PROJECT_CONFIG_DIR
    sources: List[Path] = [cfg_dir / "default.yaml"]

    if environment:
        sources.append(cfg_dir / f"{environment}.yaml")
    if mode:
        sources.append(cfg_dir / f"{mode}.yaml")
    if profile:
        sources.append(cfg_dir / f"{profile}.yaml")

    merged = load_configs(sources)

    if "mode" not in merged and mode:
        merged["mode"] = mode
    if "environment" not in merged and environment:
        merged["environment"] = environment
    if "profile" not in merged and profile:
        merged["profile"] = profile

    return Settings.from_mapping(merged, project_root=project_root)
