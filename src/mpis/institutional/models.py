"""Institutional psychology data models for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ParticipantType(str, Enum):
    """Types of institutional participants."""

    FII = "FII"
    DII = "DII"
    PRO = "PRO"
    CLIENT = "CLIENT"


class MarketState(str, Enum):
    """Market state classifications based on institutional pressure."""

    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    SLIGHT_BULLISH = "slight_bullish"
    NEUTRAL = "neutral"
    SLIGHT_BEARISH = "slight_bearish"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


class ConfidenceLevel(str, Enum):
    """Confidence tiers for institutional signals."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass(frozen=True)
class ParticipantRecord:
    """A record of institutional participant activity."""

    participant_name: str
    participant_type: ParticipantType
    equity_buy: float
    equity_sell: float
    equity_net: float
    future_buy: float
    future_sell: float
    future_net: float
    option_buy: float
    option_sell: float
    option_net: float
    oi_change: float
    volume: float

    def __post_init__(self) -> None:
        if self.equity_buy < 0.0 or self.equity_sell < 0.0:
            raise ValueError("Equity buy/sell values must be non-negative")
        if self.future_buy < 0.0 or self.future_sell < 0.0:
            raise ValueError("Future buy/sell values must be non-negative")
        if self.option_buy < 0.0 or self.option_sell < 0.0:
            raise ValueError("Option buy/sell values must be non-negative")
        if self.volume < 0.0:
            raise ValueError("Volume must be non-negative")


@dataclass(frozen=True)
class InstitutionalSignal:
    """Institutional signal generated from participant flow analysis."""

    direction: MarketState
    confidence: ConfidenceLevel
    score: float
    reason: str
    participant_scores: Mapping[str, float]


@dataclass(frozen=True)
class PsychologyResult:
    """Psychology summary from institutional participation."""

    bullish_score: float
    bearish_score: float
    neutral_score: float
    confidence: ConfidenceLevel
    state: MarketState
