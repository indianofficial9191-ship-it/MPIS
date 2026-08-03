"""Session high detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class SessionHighResult:
    """Result of session-high detection."""

    price: float
    timestamp: object
    explanation: str


class SessionHighDetector:
    """Detect the current session high."""

    def detect(self, candles: Sequence[Candle]) -> list[SessionHighResult]:
        """Return the session high as a result."""
        if not candles:
            return []

        high = max(candle.high for candle in candles)
        return [SessionHighResult(price=high, timestamp=candles[-1].timestamp, explanation="The current session high was observed.")]
