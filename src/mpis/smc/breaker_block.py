"""Breaker block detector for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from mpis.data.candle import Candle
from mpis.smc.models import BreakerBlockDirection, BreakerBlockResult
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class BreakerBlockConfig:
    """Configuration for breaker block detection."""

    invalidation_threshold: float = 0.5


class BreakerBlockDetector:
    """Detect order blocks that have been invalidated and turned into breaker blocks."""

    def __init__(self, invalidation_threshold: float = 0.5) -> None:
        self.config = BreakerBlockConfig(invalidation_threshold=invalidation_threshold)

    def detect(self, candles: Sequence[Candle], order_block: dict[str, Any] | None = None) -> list[BreakerBlockResult]:
        """Return breaker blocks based on invalidation of a prior order block."""
        if order_block is None or not candles:
            return []

        current_candle = candles[-1]
        if current_candle.close < float(order_block["low"]) - self.config.invalidation_threshold:
            direction = BreakerBlockDirection.BEARISH
            strength = min(1.0, 0.7 + self.config.invalidation_threshold)
            result = BreakerBlockResult(
                direction=direction,
                strength=strength,
                origin_block=order_block,
                timestamp=current_candle.timestamp,
            )
            logger.debug("Detected breaker block from invalidated order block")
            return [result]
        return []
