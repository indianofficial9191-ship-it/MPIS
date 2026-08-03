"""Stop hunt detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class StopHuntResult:
    """Result of stop-hunt detection."""

    direction: str
    confidence: float
    price: float
    timestamp: object


class StopHuntDetector:
    """Detect stop hunts above recent highs and below recent lows."""

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold

    def detect(self, candles: Sequence[Candle]) -> list[StopHuntResult]:
        """Return stop-hunt signals for the provided candles."""
        if len(candles) < 2:
            return []

        latest = candles[-1]
        previous_high = max(item.high for item in candles[:-1])
        previous_low = min(item.low for item in candles[:-1])

        above_move = latest.high - previous_high
        below_move = previous_low - latest.low

        if above_move >= self.threshold and above_move >= below_move:
            return [StopHuntResult(direction="above_highs", confidence=min(0.99, 0.8 + above_move / 20.0), price=latest.high, timestamp=latest.timestamp)]
        if below_move >= self.threshold and below_move > above_move:
            return [StopHuntResult(direction="below_lows", confidence=min(0.99, 0.8 + below_move / 20.0), price=latest.low, timestamp=latest.timestamp)]
        return []
