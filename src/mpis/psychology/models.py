"""Psychology data models for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Sequence


class AboveBelow(str, Enum):
    """Relative position of price to the nearest psychological level."""

    ABOVE = "above"
    BELOW = "below"
    AT = "at"


@dataclass(frozen=True)
class PsychologicalLevelsConfig:
    """Configuration for psychological level analysis."""

    symbol: str
    steps: Sequence[int]
    zone_width: float = 25.0


@dataclass(frozen=True)
class PsychologicalLevelResult:
    """Psychological level result for one step size."""

    symbol: str
    step: int
    nearest_level: float
    distance: float
    above_or_below: AboveBelow
    strength_score: float
    zone_low: float
    zone_high: float


class GapDirection(str, Enum):
    """Direction of the price gap relative to the previous close."""

    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass(frozen=True)
class PreviousDayAnalysisResult:
    """Result of previous day price and gap analysis."""

    previous_high: float
    previous_low: float
    previous_close: float
    current_open: float | None
    gap_amount: float
    gap_percent: float
    gap_direction: GapDirection
    gap_filled: bool

    @property
    def gap_up(self) -> bool:
        return self.gap_direction == GapDirection.UP

    @property
    def gap_down(self) -> bool:
        return self.gap_direction == GapDirection.DOWN


class OpeningRangeDirection(str, Enum):
    """Direction of an opening range breakout."""

    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass(frozen=True)
class OpeningRangeAnalysisResult:
    """Result of opening range analysis."""

    range_minutes: int
    opening_range_high: float
    opening_range_low: float
    range_size: float
    breakout: bool
    breakout_direction: OpeningRangeDirection
    fake_breakout: bool
    retest: bool


class FakeBreakoutType(str, Enum):
    """Types of false breakout signals."""

    FALSE_BOS = "false_bos"
    FALSE_CHOCH = "false_choch"
    FALSE_OPENING_RANGE = "false_opening_range"
    FALSE_PDH_BREAK = "false_pdh_break"
    FALSE_PDL_BREAK = "false_pdl_break"


@dataclass(frozen=True)
class FakeBreakoutConfig:
    """Configuration for fake breakout detection."""

    confirmation_candles: int = 2


@dataclass(frozen=True)
class FakeBreakoutResult:
    """Result of fake breakout detection."""

    breakout_type: FakeBreakoutType
    direction: str
    confidence: float
    trigger_price: float
    close_price: float
    timestamp: datetime
    explanation: str


class LiquidityGrabDirection(str, Enum):
    """Direction of a liquidity grab event."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NONE = "none"


@dataclass(frozen=True)
class LiquidityGrabConfig:
    """Configuration for liquidity grab detection."""

    body_threshold: float = 0.15
    wick_threshold: float = 0.25
    sweep_threshold: float = 0.5


@dataclass(frozen=True)
class LiquidityGrabResult:
    """Result of liquidity grab detection."""

    found: bool
    direction: LiquidityGrabDirection
    confidence: float
    sweep_price: float | None
    rejection_price: float | None
    close_back_inside: bool
    explanation: str


class WickAnalysisClassification(str, Enum):
    """Classification of wick-based rejection signals."""

    BULLISH_REJECTION = "bullish_rejection"
    BEARISH_REJECTION = "bearish_rejection"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class WickAnalysisResult:
    """Result of wick analysis for a single candle."""

    upper_wick_pct: float
    lower_wick_pct: float
    body_pct: float
    classification: WickAnalysisClassification


class TrendStrength(str, Enum):
    """Market trend strength categories."""

    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    WEAK_BEARISH = "weak_bearish"
    SIDEWAYS = "sideways"
    WEAK_BULLISH = "weak_bullish"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


@dataclass(frozen=True)
class TrendContext:
    """Contextual trend strength signals from structure and swing analysis."""

    trend: TrendStrength
    confidence: float
    bos_confirmed: bool
    choch_confirmed: bool
    mss_confirmed: bool
    swing_highs: list[float]
    swing_lows: list[float]
    timestamp: datetime


class TrapType(str, Enum):
    """Types of trap signals detected."""

    BULL_TRAP = "bull_trap"
    BEAR_TRAP = "bear_trap"
    NONE = "none"


@dataclass(frozen=True)
class TrapConfig:
    """Configuration for trap detection."""

    confirmation_candles: int = 2
    minimum_confidence: float = 0.5


@dataclass(frozen=True)
class TrapResult:
    """Result of trap detection."""

    trap_type: TrapType
    confidence: float
    liquidity_detected: bool
    structure_detected: bool
    rejection_detected: bool
    explanation: str


class PsychologyEngineResult:
    """Container for psychology engine analysis results."""

    def __init__(
        self,
        psychological_levels: list[PsychologicalLevelResult],
        previous_day: PreviousDayAnalysisResult | None,
        opening_range: OpeningRangeAnalysisResult | None,
        session: "SessionResult",
    ) -> None:
        self.psychological_levels = psychological_levels
        self.previous_day = previous_day
        self.opening_range = opening_range
        self.session = session
