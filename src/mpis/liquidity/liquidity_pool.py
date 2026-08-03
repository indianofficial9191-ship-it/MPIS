"""Liquidity pool detector for the liquidity engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.models import LiquidityPoolResult


@dataclass(frozen=True)
class LiquidityPoolConfig:
    """Configuration for liquidity pool detection."""

    lookback: int = 3
    minimum_touches: int = 2
    price_tolerance: float = 0.3
    confidence_threshold: float = 0.75


class LiquidityPoolDetector:
    """Cluster nearby equal highs and equal lows into a liquidity pool."""

    def __init__(self, config: LiquidityPoolConfig | None = None) -> None:
        self.config = config or LiquidityPoolConfig()

    def detect(self, candles: Sequence[Candle]) -> list[LiquidityPoolResult]:
        """Return liquidity pool signals from the candle sequence."""
        if len(candles) < self.config.lookback:
            return []

        window = list(candles[-self.config.lookback:])
        prices = [candle.close for candle in window]
        average = sum(prices) / len(prices)
        touches = sum(1 for value in prices if abs(value - average) <= self.config.price_tolerance)
        if touches < self.config.minimum_touches:
            return []

        strength = min(1.0, 0.7 + (touches / max(1, len(prices))) * 0.3)
        if strength < self.config.confidence_threshold:
            return []

        direction = "buy_side" if average >= prices[0] else "sell_side"
        return [
            LiquidityPoolResult(
                pool_price=average,
                pool_size=touches,
                strength=strength,
                confidence=strength,
                price=average,
                direction=direction,
                liquidity_level="resting",
                touch_count=touches,
                explanation="Nearby candles cluster around a shared price level, implying resting liquidity.",
                timestamp=candles[-1].timestamp,
            )
        ]
