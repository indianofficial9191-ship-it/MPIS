"""Unified Smart Money Concepts engine."""
from __future__ import annotations

from typing import Sequence

from mpis.data.candle import Candle
from mpis.smc.breaker_block import BreakerBlockDetector
from mpis.smc.fvg import BullishFVGDetector, BearishFVGDetector
from mpis.smc.imbalance import ImbalanceDetector
from mpis.smc.mitigation_block import MitigationBlockDetector
from mpis.smc.models import SMCEngineResult
from mpis.smc.order_block import OrderBlockDetector
from mpis.utils.logger import get_logger

logger = get_logger(__name__)


class SMCEngine:
    """Run the Smart Money Concepts detectors through a single API."""

    def __init__(self) -> None:
        self.fvg_bullish_detector = BullishFVGDetector()
        self.fvg_bearish_detector = BearishFVGDetector()
        self.imbalance_detector = ImbalanceDetector()
        self.order_block_detector = OrderBlockDetector()
        self.breaker_block_detector = BreakerBlockDetector()
        self.mitigation_block_detector = MitigationBlockDetector()

    def analyze(self, buffer: Sequence[Candle]) -> SMCEngineResult:
        """Analyze a candle buffer and return all SMC components."""
        fvgs = []
        fvgs.extend(self.fvg_bullish_detector.detect(list(buffer)))
        fvgs.extend(self.fvg_bearish_detector.detect(list(buffer)))

        imbalances = self.imbalance_detector.detect(list(buffer))
        order_blocks = self.order_block_detector.detect(list(buffer))
        breaker_blocks = []
        if order_blocks:
            breaker_blocks.extend(self.breaker_block_detector.detect(list(buffer), order_block={
                "direction": order_blocks[0].direction,
                "high": order_blocks[0].high,
                "low": order_blocks[0].low,
                "strength": order_blocks[0].strength,
                "timestamp": order_blocks[0].timestamp,
            }))

        mitigation_blocks = self.mitigation_block_detector.detect(list(buffer), reference_price=buffer[-1].close)
        logger.info("SMC engine analyzed %d candles", len(buffer))
        return SMCEngineResult(
            fvgs=tuple(fvgs),
            imbalances=tuple(imbalances),
            order_blocks=tuple(order_blocks),
            breaker_blocks=tuple(breaker_blocks),
            mitigation_blocks=tuple(mitigation_blocks),
        )
