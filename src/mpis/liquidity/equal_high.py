"""Equal-high detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class EqualHighResult:
    """Result of equal-high detection."""

    price: float
    tolerance: float
    timestamp: object


class EqualHighDetector:
    """Detect repeated equal highs within a tolerance."""

    def __init__(self, tolerance: float = 0.5) -> None:
        self.tolerance = tolerance

    def detect(self, candles: Sequence[Candle]) -> list[EqualHighResult]:
        """Return equal-high signals for the provided candles."""
        if len(candles) < 2:
            return []
        highs = [candle.high for candle in candles]
        reference = max(highs)
        if not highs:
            return []

        matching = [high for high in highs if abs(high - reference) <= self.tolerance]
        if len(matching) < 2:
            return []

        detected_price = min(matching)
        return [EqualHighResult(price=detected_price, tolerance=self.tolerance, timestamp=candles[-1].timestamp)]
