"""Core models for Open Interest and derivatives intelligence in MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Direction(str, Enum):
    """Direction signal for open interest market conditions."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class ConfidenceLevel(str, Enum):
    """Confidence tier for open interest signals."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PositionType(str, Enum):
    """Position type for open interest classification."""

    LONG_BUILDUP = "long_buildup"
    SHORT_BUILDUP = "short_buildup"
    LONG_UNWINDING = "long_unwinding"
    SHORT_COVERING = "short_covering"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ParticipantOIRecord:
    """A record of open interest activity for a market participant."""

    participant_name: str
    participant_type: str
    long_oi: float
    short_oi: float
    long_change: float
    short_change: float
    volume: float
    net_oi: float

    def __post_init__(self) -> None:
        if self.long_oi < 0.0:
            raise ValueError("long_oi must be non-negative")
        if self.short_oi < 0.0:
            raise ValueError("short_oi must be non-negative")
        if self.long_change < 0.0 and self.short_change < 0.0 and self.net_oi > 0.0:
            raise ValueError("net_oi cannot be positive when both long and short changes are negative")
        if self.volume < 0.0:
            raise ValueError("volume must be non-negative")


@dataclass(frozen=True)
class OISignal:
    """Signal describing open interest market direction and conviction."""

    direction: Direction
    confidence: ConfidenceLevel
    score: float
    reason: str
    participant_scores: Mapping[str, float]


@dataclass(frozen=True)
class PositionSignal:
    """Signal describing the dominant open interest position type."""

    position_type: PositionType
    strength: float
    confidence: ConfidenceLevel
    reason: str
