"""Imbalance detector for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.smc.models import ImbalanceDirection, ImbalanceResult
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ImbalanceConfig:
    """Configuration for imbalance detection."""

    min_body_ratio: float = 0.6
    min_range_ratio: float = 0.4


class ImbalanceDetector:
    """Detect large displacement candles with a strong body-to-range ratio."""

    def __init__(self, min_body_ratio: float = 0.6, min_range_ratio: float = 0.4) -> None:
        self.config = ImbalanceConfig(min_body_ratio=min_body_ratio, min_range_ratio=min_range_ratio)

    def detect(self, candles: Sequence[Candle]) -> list[ImbalanceResult]:
        """Return imbalance signals from a candle sequence."""
        if len(candles) < 2:
            return []

        candle = candles[-1]
        body_ratio = candle.body / max(candle.range, 1e-9)
        previous_range = max(candles[-2].range, 1e-9) if len(candles) > 1 else 1.0
        range_ratio = candle.range / previous_range
        if body_ratio < self.config.min_body_ratio * 0.5 and range_ratio < max(self.config.min_range_ratio * 1.5, 1.2):
            return []

        direction = ImbalanceDirection.BULLISH if candle.close >= candle.open else ImbalanceDirection.BEARISH
        result = ImbalanceResult(
            direction=direction,
            body_ratio=body_ratio,
            range_ratio=range_ratio,
            momentum_score=min(1.0, 0.5 * body_ratio + 0.5 * range_ratio),
            timestamp=candle.timestamp,
        )
        logger.debug("Detected %s imbalance with momentum %.3f", direction.value, result.momentum_score)
        return [result]
