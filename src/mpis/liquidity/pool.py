"""Liquidity pool detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class LiquidityPoolConfig:
    """Configuration for liquidity pool detection."""

    lookback: int = 3
    minimum_touches: int = 2
    price_tolerance: float = 0.3
    confidence_threshold: float = 0.75


@dataclass(frozen=True)
class LiquidityPoolResult:
    """Result of liquidity pool detection."""

    direction: str
    liquidity_level: str
    touch_count: int
    confidence: float
    explanation: str
    timestamp: object


class LiquidityPoolDetector:
    """Detect clustered buying or selling interest around a shared price level."""

    def __init__(self, config: LiquidityPoolConfig | None = None) -> None:
        self.config = config or LiquidityPoolConfig()

    def detect(self, candles: Sequence[Candle]) -> list[LiquidityPoolResult]:
        """Return liquidity pool results from a candle sequence."""
        if len(candles) < 2:
            return []

        values = [candle.close for candle in candles[-self.config.lookback:]]
        average = sum(values) / len(values)
        touches = sum(1 for value in values if abs(value - average) <= self.config.price_tolerance)
        if touches < self.config.minimum_touches:
            return []

        confidence = min(1.0, 0.7 + (touches / max(1, len(values))) * 0.3)
        if confidence < self.config.confidence_threshold:
            return []

        direction = "buy_side" if average >= values[0] else "sell_side"
        liquidity_level = "resting" if touches >= self.config.minimum_touches else "thin"
        return [
            LiquidityPoolResult(
                direction=direction,
                liquidity_level=liquidity_level,
                touch_count=touches,
                confidence=confidence,
                explanation="Recent candles cluster around a shared price level, indicating resting liquidity.",
                timestamp=candles[-1].timestamp,
            )
        ]
