"""Market structure models for swing analysis in MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class SwingDirection(str, Enum):
    """Direction of a market swing."""

    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class SwingType(str, Enum):
    """The type of an identified swing point."""

    HIGH = "high"
    LOW = "low"


class SwingStrength(str, Enum):
    """The strength classification of a swing point."""

    WEAK = "weak"
    STRONG = "strong"


@dataclass(frozen=True)
class SwingPoint:
    """A pivot point in market structure representing a swing high or low."""

    index: int
    timestamp: datetime
    price: float
    type: SwingType
    strength: SwingStrength


@dataclass(frozen=True)
class Swing:
    """Represents a price swing in market structure."""

    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    direction: SwingDirection
    magnitude: float
