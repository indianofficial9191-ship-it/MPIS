"""Round-number psychology detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class RoundNumberPsychologyResult:
    """Result of round-number psychology detection."""

    confidence: float
    price: float
    timestamp: object
    explanation: str


class RoundNumberPsychologyDetector:
    """Detect when price is near a round number level."""

    def __init__(self, tolerance: float = 0.5) -> None:
        self.tolerance = tolerance

    def detect(self, candles: Sequence[Candle]) -> list[RoundNumberPsychologyResult]:
        """Return a signal when the latest close is near a round number."""
        if not candles:
            return []

        current = candles[-1].close
        rounded = round(current)
        if abs(current - rounded) <= self.tolerance:
            return [
                RoundNumberPsychologyResult(
                    confidence=0.9,
                    price=rounded,
                    timestamp=candles[-1].timestamp,
                    explanation="Price is near a psychologically important round number.",
                )
            ]
        return []
