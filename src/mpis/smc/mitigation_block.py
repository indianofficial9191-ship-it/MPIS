"""Mitigation block detector for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.smc.models import MitigationBlockResult, MitigationStatus
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class MitigationBlockConfig:
    """Configuration for mitigation block detection."""

    threshold: float = 0.25


class MitigationBlockDetector:
    """Detect revisit or mitigation of a prior price level."""

    def __init__(self, threshold: float = 0.25) -> None:
        self.config = MitigationBlockConfig(threshold=threshold)

    def detect(self, candles: Sequence[Candle], reference_price: float) -> list[MitigationBlockResult]:
        """Return mitigation signal when a candle revisits the reference price."""
        if len(candles) < 2:
            return []

        current_candle = candles[-1]
        if current_candle.low <= reference_price <= current_candle.high:
            distance = abs(current_candle.close - reference_price)
            status = MitigationStatus.PARTIAL if distance > self.config.threshold else MitigationStatus.FULL
            result = MitigationBlockResult(
                status=status,
                strength_score=min(1.0, 0.5 + distance),
                reference_price=reference_price,
                timestamp=current_candle.timestamp,
            )
            logger.debug("Detected mitigation block with status %s", status.value)
            return [result]
        return []
