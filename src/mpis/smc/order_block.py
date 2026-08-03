"""Order block detector for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.smc.models import OrderBlockDirection, OrderBlockResult
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class OrderBlockConfig:
    """Configuration for order block detection."""

    min_body_ratio: float = 0.5
    freshness_window: int = 3
    max_retests: int = 2


class OrderBlockDetector:
    """Detect bullish and bearish order blocks from strong reversal candles."""

    def __init__(self, min_body_ratio: float = 0.5, freshness_window: int = 3, max_retests: int = 2) -> None:
        self.config = OrderBlockConfig(min_body_ratio=min_body_ratio, freshness_window=freshness_window, max_retests=max_retests)

    def detect(self, candles: Sequence[Candle]) -> list[OrderBlockResult]:
        """Return order blocks from a candle sequence."""
        if len(candles) < 4:
            return []

        for anchor_index in range(max(0, len(candles) - 3), len(candles) - 1):
            anchor_candle = candles[anchor_index]
            displacement_candle = candles[anchor_index + 1]
            body_ratio = anchor_candle.body / max(anchor_candle.range, 1e-9)
            if body_ratio < max(self.config.min_body_ratio * 0.4, 0.2):
                continue

            if anchor_candle.close > anchor_candle.open and displacement_candle.close <= anchor_candle.high:
                direction = OrderBlockDirection.BULLISH
                high = max(anchor_candle.high, displacement_candle.high)
                low = min(anchor_candle.low, displacement_candle.low)
                strength = min(1.0, body_ratio + 0.1)
                result = OrderBlockResult(
                    direction=direction,
                    high=high,
                    low=low,
                    strength=strength,
                    freshness=1,
                    retest_count=0,
                    validity="valid",
                    timestamp=displacement_candle.timestamp,
                    origin_candle=anchor_candle.timestamp,
                )
                logger.debug("Detected bullish order block with strength %.3f", result.strength)
                return [result]

            if anchor_candle.close < anchor_candle.open and displacement_candle.close >= anchor_candle.low:
                direction = OrderBlockDirection.BEARISH
                high = max(anchor_candle.high, displacement_candle.high)
                low = min(anchor_candle.low, displacement_candle.low)
                result = OrderBlockResult(
                    direction=direction,
                    high=high,
                    low=low,
                    strength=min(1.0, body_ratio),
                    freshness=1,
                    retest_count=0,
                    validity="valid",
                    timestamp=displacement_candle.timestamp,
                    origin_candle=anchor_candle.timestamp,
                )
                logger.debug("Detected bearish order block with strength %.3f", result.strength)
                return [result]
        return []
