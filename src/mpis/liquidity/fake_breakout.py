"""Fake breakout detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class FakeBreakoutResult:
    """Result of fake breakout detection."""

    direction: str
    confidence: float
    price: float
    timestamp: object
    explanation: str


class FakeBreakoutDetector:
    """Detect a breakout that quickly fails and retraces."""

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold

    def detect(self, candles: Sequence[Candle]) -> list[FakeBreakoutResult]:
        """Return a fake breakout signal when price breaks above recent resistance and then closes back inside."""
        if len(candles) < 3:
            return []

        previous = candles[-2]
        current = candles[-1]
        if current.high > previous.high + self.threshold and current.close < previous.high + self.threshold * 2.0:
            return [
                FakeBreakoutResult(
                    direction="up",
                    confidence=0.9,
                    price=current.close,
                    timestamp=current.timestamp,
                    explanation="Price briefly broke above a prior high before failing to hold.",
                )
            ]
        return []
