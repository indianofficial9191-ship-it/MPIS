"""Swing liquidity detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class SwingLiquidityConfig:
    """Configuration for swing liquidity detection."""

    lookback: int = 2
    minimum_swing_distance: float = 1.0


@dataclass(frozen=True)
class SwingLiquidityResult:
    """Result of swing liquidity detection."""

    direction: str
    confidence: float
    price: float
    explanation: str
    timestamp: object


class SwingLiquidityDetector:
    """Detect liquidity resting above swing highs or below swing lows."""

    def __init__(self, config: SwingLiquidityConfig | None = None) -> None:
        self.config = config or SwingLiquidityConfig()

    def detect(self, candles: Sequence[Candle]) -> list[SwingLiquidityResult]:
        """Return swing liquidity results from candles."""
        if len(candles) < self.config.lookback + 1:
            return []

        reference = candles[-self.config.lookback - 1]
        latest = candles[-1]
        distance = latest.high - reference.high
        if distance >= self.config.minimum_swing_distance:
            return [
                SwingLiquidityResult(
                    direction="above_swing_high",
                    confidence=0.9,
                    price=latest.high,
                    explanation="Price moved beyond the previous swing high with significant distance.",
                    timestamp=latest.timestamp,
                )
            ]
        if reference.low - latest.low >= self.config.minimum_swing_distance:
            return [
                SwingLiquidityResult(
                    direction="below_swing_low",
                    confidence=0.9,
                    price=latest.low,
                    explanation="Price moved beyond the previous swing low with significant distance.",
                    timestamp=latest.timestamp,
                )
            ]
        return []
