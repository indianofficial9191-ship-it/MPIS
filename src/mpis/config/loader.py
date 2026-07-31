"""YAML loader and merging logic for MPIS configuration."""
from __future__ import annotations

import yaml
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from .constants import PROJECT_CONFIG_DIR


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise TypeError(f"Config file {path} must contain a mapping at top-level")
        return data


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge mapping `b` into `a` and return result.

    Values from `b` override those from `a`.
    """
    result = deepcopy(a)
    for k, v in b.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def load_configs(sources: List[Path]) -> Dict[str, Any]:
    """Load and merge YAML configuration files from `sources` in order.

    Later sources override earlier ones.
    """
    merged: Dict[str, Any] = {}
    for src in sources:
        merged = deep_merge(merged, _safe_load_yaml(src))
    return merged


def default_config_paths(config_dir: Path | None = None) -> List[Path]:
    cfg_dir = (config_dir or PROJECT_CONFIG_DIR)
    return [cfg_dir / "default.yaml"]
