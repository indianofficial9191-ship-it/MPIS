"""Inducement detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class InducementResult:
    """Result of inducement detection."""

    confidence: float
    price: float
    timestamp: object
    explanation: str


class InducementDetector:
    """Detect a retest or false move that entices traders into a position."""

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold

    def detect(self, candles: Sequence[Candle]) -> list[InducementResult]:
        """Return an inducement signal when price revisits a prior level after a breakout."""
        if len(candles) < 3:
            return []

        previous = candles[-2]
        current = candles[-1]
        if abs(current.close - previous.high) <= self.threshold:
            return [
                InducementResult(
                    confidence=0.85,
                    price=current.close,
                    timestamp=current.timestamp,
                    explanation="Price re-tested a prior breakout level, creating inducement.",
                )
            ]
        return []
