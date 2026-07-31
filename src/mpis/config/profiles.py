"""Market profile definitions and helpers."""
from __future__ import annotations

from enum import Enum


class Profile(Enum):
    """Supported market profiles."""

    NIFTY = "nifty"
    BANKNIFTY = "banknifty"

    @classmethod
    def from_str(cls, value: str) -> "Profile":
        """Convert a string to a `Profile` (case-insensitive)."""
        val = value.strip().lower()
        for member in cls:
            if member.value == val:
                return member
        raise ValueError(f"Unsupported profile: {value}")
