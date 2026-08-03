"""Grab detector for the liquidity engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.models import GrabResult


@dataclass(frozen=True)
class GrabConfig:
    """Configuration for grab detection."""

    body_threshold: float = 0.1
    wick_threshold: float = 0.35


class GrabDetector:
    """Detect a candle that grabs liquidity with a strong body and long wick."""

    def __init__(self, config: GrabConfig | None = None) -> None:
        self.config = config or GrabConfig()

    def detect(self, candles: Sequence[Candle]) -> list[GrabResult]:
        """Return grab signals for the latest candle."""
        if not candles:
            return []

        current = candles[-1]
        body = abs(current.close - current.open)
        wick = max(current.high - max(current.open, current.close), min(current.open, current.close) - current.low)
        range_size = current.high - current.low
        if range_size == 0:
            return []

        if body >= self.config.body_threshold * range_size and wick >= self.config.wick_threshold * range_size:
            direction = "bullish" if current.close >= current.open else "bearish"
            confidence = min(1.0, 0.7 + body / range_size * 0.2 + wick / range_size * 0.4)
            return [
                GrabResult(
                    direction=direction,
                    confidence=confidence,
                    sweep_price=current.high if direction == "bullish" else current.low,
                    rejection_price=current.close,
                    momentum_price=current.close,
                    explanation="A candle with a strong body and extended wick suggests aggressive liquidity grabbing.",
                    timestamp=current.timestamp,
                )
            ]
        return []
