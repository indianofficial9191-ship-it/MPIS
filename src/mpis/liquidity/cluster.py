"""Liquidity cluster detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle


@dataclass(frozen=True)
class LiquidityClusterResult:
    """Result of nearby swing-price clustering."""

    cluster_center: float
    cluster_size: int
    confidence: float
    explanation: str
    timestamp: object


class LiquidityClusterDetector:
    """Detect nearby swing highs or swing lows that cluster around a common level."""

    def __init__(self, tolerance: float = 0.6) -> None:
        self.tolerance = tolerance

    def detect(self, candles: Sequence[Candle]) -> list[LiquidityClusterResult]:
        """Return liquidity cluster results from the candle sequence."""
        if len(candles) < 2:
            return []

        highs = [candle.high for candle in candles]
        lows = [candle.low for candle in candles]
        high_center = sum(highs) / len(highs)
        low_center = sum(lows) / len(lows)
        high_cluster = sum(1 for high in highs if abs(high - high_center) <= self.tolerance)
        low_cluster = sum(1 for low in lows if abs(low - low_center) <= self.tolerance)

        if high_cluster >= 2:
            return [
                LiquidityClusterResult(
                    cluster_center=high_center,
                    cluster_size=high_cluster,
                    confidence=0.9,
                    explanation="Multiple nearby highs cluster around a shared price area.",
                    timestamp=candles[-1].timestamp,
                )
            ]
        if low_cluster >= 2:
            return [
                LiquidityClusterResult(
                    cluster_center=low_center,
                    cluster_size=low_cluster,
                    confidence=0.9,
                    explanation="Multiple nearby lows cluster around a shared price area.",
                    timestamp=candles[-1].timestamp,
                )
            ]
        return []
