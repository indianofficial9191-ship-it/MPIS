"""Market structure models for swing analysis in MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from mpis.data.candle import Candle


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


class StructureType(str, Enum):
    """Market structure signal type."""

    BOS = "bos"
    CHOCH = "choch"
    MSS = "mss"


class TrendState(str, Enum):
    """Market trend state."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    RANGE = "range"


@dataclass(frozen=True)
class SwingPoint:
    """A pivot point in market structure representing a swing high or low."""

    index: int
    timestamp: datetime
    price: float
    type: SwingType
    strength: SwingStrength


@dataclass(frozen=True)
class StructureSignal:
    """Represents a detected structure signal in market analysis."""

    index: int
    timestamp: datetime
    price: float
    type: StructureType
    direction: str
    strength: float
    candle: Candle | None = None


@dataclass(frozen=True)
class StructureBreak:
    """Represents a structure break event."""

    signal: StructureSignal
    break_price: float
    break_time: datetime
    direction: TrendState


@dataclass(frozen=True)
class TrendAnalysis:
    """Trend detection result for market structure analysis."""

    trend: TrendState
    higher_high: bool
    higher_low: bool
    lower_high: bool
    lower_low: bool


@dataclass(frozen=True)
class Swing:
    """Represents a price swing in market structure."""

    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    direction: SwingDirection
    magnitude: float
