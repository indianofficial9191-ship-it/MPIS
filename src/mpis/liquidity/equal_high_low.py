"""Equal-high and equal-low detectors for the liquidity engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.models import EqualHighResult, EqualLowResult


@dataclass(frozen=True)
class EqualHighConfig:
    """Configuration for equal-high detection."""

    tolerance: float = 0.3
    minimum_touches: int = 2


@dataclass(frozen=True)
class EqualLowConfig:
    """Configuration for equal-low detection."""

    tolerance: float = 0.3
    minimum_touches: int = 2


class EqualHighDetector:
    """Detect clustered equal highs within a price tolerance."""

    def __init__(self, tolerance: float = 0.3, minimum_touches: int = 2) -> None:
        self.config = EqualHighConfig(tolerance=tolerance, minimum_touches=minimum_touches)

    def detect(self, candles: Sequence[Candle]) -> list[EqualHighResult]:
        """Return equal-high clusters found in the candle sequence."""
        if len(candles) < self.config.minimum_touches:
            return []

        highs = [candle.high for candle in candles]
        reference = max(highs)
        indexes = tuple(index for index, value in enumerate(highs) if abs(value - reference) <= self.config.tolerance)
        if len(indexes) < self.config.minimum_touches:
            return []

        strength = min(1.0, 0.6 + (len(indexes) / max(1, len(candles))) * 0.4)
        detected_price = min(high for index, high in enumerate(highs) if index in indexes)
        return [
            EqualHighResult(
                price=detected_price,
                tolerance=self.config.tolerance,
                strength=strength,
                touch_count=len(indexes),
                indexes=indexes,
                explanation="Multiple highs clustered within the configured tolerance.",
                timestamp=candles[-1].timestamp,
            )
        ]


class EqualLowDetector:
    """Detect clustered equal lows within a price tolerance."""

    def __init__(self, tolerance: float = 0.3, minimum_touches: int = 2) -> None:
        self.config = EqualLowConfig(tolerance=tolerance, minimum_touches=minimum_touches)

    def detect(self, candles: Sequence[Candle]) -> list[EqualLowResult]:
        """Return equal-low clusters found in the candle sequence."""
        if len(candles) < self.config.minimum_touches:
            return []

        lows = [candle.low for candle in candles]
        reference = min(lows)
        indexes = tuple(index for index, value in enumerate(lows) if abs(value - reference) <= self.config.tolerance)
        if len(indexes) < self.config.minimum_touches:
            return []

        strength = min(1.0, 0.6 + (len(indexes) / max(1, len(candles))) * 0.4)
        detected_price = min(low for index, low in enumerate(lows) if index in indexes)
        return [
            EqualLowResult(
                price=detected_price,
                tolerance=self.config.tolerance,
                strength=strength,
                touch_count=len(indexes),
                indexes=indexes,
                explanation="Multiple lows clustered within the configured tolerance.",
                timestamp=candles[-1].timestamp,
            )
        ]
