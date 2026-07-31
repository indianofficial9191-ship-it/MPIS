"""Validation utilities for MPIS configuration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""


def _type_name(value: Any) -> str:
    return type(value).__name__


def validate_keys(config: Dict[str, Any], required: Dict[str, type]) -> None:
    """Validate that required keys exist in `config` and are of correct type.

    Args:
        config: Parsed configuration mapping.
        required: Mapping of key names to expected types.

    Raises:
        ConfigurationError: if a required key is missing or has wrong type.
    """
    for key, expected in required.items():
        if key not in config:
            raise ConfigurationError(f"Missing required config key: {key}")
        val = config[key]
        if not isinstance(val, expected):
            raise ConfigurationError(
                f"Invalid type for key '{key}': expected {expected.__name__}, got {_type_name(val)}"
            )
