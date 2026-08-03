"""Session high/low detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Sequence

from mpis.data.candle import Candle


class SessionType(str, Enum):
    """Supported trading sessions."""

    ASIAN = "asian"
    EUROPEAN = "european"
    US = "us"
    INDIAN = "indian"


@dataclass(frozen=True)
class SessionResult:
    """Result of session high/low detection."""

    session: SessionType
    session_start: datetime
    session_end: datetime
    high: float
    low: float
    breaks: list[tuple[float, datetime]]
    explanation: str


class SessionDetector:
    """Track session high/low levels for supported market sessions."""

    def detect(self, candles: Sequence[Candle], session_type: SessionType) -> SessionResult | None:
        """Return the session result for a sequence of candles."""
        if not candles:
            return None

        start = candles[0].timestamp
        end = candles[-1].timestamp
        highs = [candle.high for candle in candles]
        lows = [candle.low for candle in candles]
        breaks = [(candle.high, candle.timestamp) for candle in candles if candle.high >= max(highs) - 1e-9]

        return SessionResult(
            session=session_type,
            session_start=start,
            session_end=end,
            high=max(highs),
            low=min(lows),
            breaks=breaks,
            explanation=f"Tracked {session_type.value} session high/low levels.",
        )
