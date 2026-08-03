"""Fair Value Gap detectors for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.smc.models import FVGDirection, FVGResult, FVGStatus
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FVGConfig:
    """Configuration for FVG detection."""

    min_gap: float = 0.5
    fill_percentage: float = 0.5


class BullishFVGDetector:
    """Detect bullish fair value gaps from three-candle structures."""

    def __init__(self, min_gap: float = 0.5, fill_percentage: float = 0.5) -> None:
        self.config = FVGConfig(min_gap=min_gap, fill_percentage=fill_percentage)

    def detect(self, candles: Sequence[Candle]) -> list[FVGResult]:
        """Return bullish FVGs for a sequence of candles."""
        if len(candles) < 3:
            return []

        first, second, third = candles[-3], candles[-2], candles[-1]
        gap_size = second.high - first.low
        if gap_size < self.config.min_gap:
            return []

        if first.low <= third.close <= second.high:
            fill_ratio = min(1.0, max(0.0, (third.close - first.low) / max(gap_size, 1e-9)))
            status = FVGStatus.ACTIVE if fill_ratio <= self.config.fill_percentage else FVGStatus.FILLED
            result = FVGResult(
                direction=FVGDirection.BULLISH,
                gap_size=gap_size,
                fill_percentage=fill_ratio,
                status=status,
                strength=min(1.0, gap_size / max(second.range, 1.0)),
                timestamp=third.timestamp,
                low=first.low,
                high=second.high,
            )
            logger.debug("Detected bullish FVG with strength %.3f", result.strength)
            return [result]
        return []


class BearishFVGDetector:
    """Detect bearish fair value gaps from three-candle structures."""

    def __init__(self, min_gap: float = 0.5, fill_percentage: float = 0.5) -> None:
        self.config = FVGConfig(min_gap=min_gap, fill_percentage=fill_percentage)

    def detect(self, candles: Sequence[Candle]) -> list[FVGResult]:
        """Return bearish FVGs for a sequence of candles."""
        if len(candles) < 3:
            return []

        first, second, third = candles[-3], candles[-2], candles[-1]
        gap_size = first.high - second.low
        if gap_size < self.config.min_gap:
            return []

        if second.low <= third.close <= first.high:
            fill_ratio = min(1.0, max(0.0, (first.high - third.close) / max(gap_size, 1e-9)))
            status = FVGStatus.ACTIVE if fill_ratio <= self.config.fill_percentage else FVGStatus.FILLED
            result = FVGResult(
                direction=FVGDirection.BEARISH,
                gap_size=gap_size,
                fill_percentage=fill_ratio,
                status=status,
                strength=min(1.0, gap_size / max(second.range, 1.0)),
                timestamp=third.timestamp,
                low=second.low,
                high=first.high,
            )
            logger.debug("Detected bearish FVG with strength %.3f", result.strength)
            return [result]
        return []
