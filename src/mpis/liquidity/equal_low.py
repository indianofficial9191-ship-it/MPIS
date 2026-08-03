"""Equal-low detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class EqualLowResult:
    """Result of equal-low detection."""

    price: float
    tolerance: float
    timestamp: object


class EqualLowDetector:
    """Detect repeated equal lows within a tolerance."""

    def __init__(self, tolerance: float = 0.5) -> None:
        self.tolerance = tolerance

    def detect(self, candles: Sequence[Candle]) -> list[EqualLowResult]:
        """Return equal-low signals for the provided candles."""
        if len(candles) < 2:
            return []
        lows = [candle.low for candle in candles]
        reference = min(lows)
        if not lows:
            return []

        matching = [low for low in lows if abs(low - reference) <= self.tolerance]
        if len(matching) < 2:
            return []

        detected_price = min(matching)
        return [EqualLowResult(price=detected_price, tolerance=self.tolerance, timestamp=candles[-1].timestamp)]
