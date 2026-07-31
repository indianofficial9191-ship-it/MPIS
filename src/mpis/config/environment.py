"""Environment definitions for MPIS configuration."""
from __future__ import annotations

from enum import Enum


class Environment(Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    @classmethod
    def from_str(cls, value: str) -> "Environment":
        """Return the Environment for a string value (case-insensitive)."""
        val = value.strip().lower()
        for member in cls:
            if member.value == val:
                return member
        raise ValueError(f"Unsupported environment: {value}")
