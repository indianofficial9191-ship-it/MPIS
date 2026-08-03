"""Session low detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class SessionLowResult:
    """Result of session-low detection."""

    price: float
    timestamp: object
    explanation: str


class SessionLowDetector:
    """Detect the current session low."""

    def detect(self, candles: Sequence[Candle]) -> list[SessionLowResult]:
        """Return the session low as a result."""
        if not candles:
            return []

        low = min(candle.low for candle in candles)
        return [SessionLowResult(price=low, timestamp=candles[-1].timestamp, explanation="The current session low was observed.")]
