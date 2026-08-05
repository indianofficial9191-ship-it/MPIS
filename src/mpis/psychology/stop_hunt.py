"""Stop-hunt detection for MPIS psychology sprint 5B."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Sequence

from mpis.data.candle import Candle

logger = logging.getLogger(__name__)


class StopHuntSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class StopHuntConfig:
    min_wick_pct: float = 30.0  # wick as percent of candle range
    min_penetration_pct: float = 10.0  # penetration into previous candle body percent


@dataclass(frozen=True)
class StopHuntResult:
    found: bool
    side: StopHuntSide | None
    confidence: float
    wick_pct: float
    penetration_pct: float
    explanation: str


class StopHuntDetector:
    """Detect stop-loss hunts (buy-side or sell-side) using wick and penetration heuristics."""

    def __init__(self, config: StopHuntConfig | None = None) -> None:
        self.config = config or StopHuntConfig()

    def detect(self, candles: Sequence[Candle]) -> list[StopHuntResult]:
        """Return a list of detected stop hunts in the candle sequence.

        The detector looks for large wicks relative to range and penetration into the prior candle's body.
        """
        results: list[StopHuntResult] = []
        if len(candles) < 2:
            return results

        for i in range(1, len(candles)):
            prev = candles[i - 1]
            cur = candles[i]
            rng = cur.range if cur.range > 0 else 1.0
            upper_wick_pct = (cur.upper_wick / rng) * 100.0
            lower_wick_pct = (cur.lower_wick / rng) * 100.0

            # penetration into previous body: how much the wick extends into prev open-close body
            prev_body_high = max(prev.open, prev.close)
            prev_body_low = min(prev.open, prev.close)

            penetration_pct = 0.0
            side: StopHuntSide | None = None
            found = False

            # buy side hunt: long lower wick that penetrates previous body
            if lower_wick_pct >= self.config.min_wick_pct:
                penetration = max(0.0, prev_body_low - cur.low) if cur.low < prev_body_low else 0.0
                penetration_pct = (penetration / rng) * 100.0
                if penetration_pct >= self.config.min_penetration_pct and cur.close > cur.open:
                    found = True
                    side = StopHuntSide.BUY

            # sell side hunt: long upper wick
            if not found and upper_wick_pct >= self.config.min_wick_pct:
                penetration = max(0.0, cur.high - prev_body_high) if cur.high > prev_body_high else 0.0
                penetration_pct = (penetration / rng) * 100.0
                if penetration_pct >= self.config.min_penetration_pct and cur.close < cur.open:
                    found = True
                    side = StopHuntSide.SELL

            confidence = 0.0
            if found:
                # confidence scales by wick_pct and penetration_pct, clipped to 0..1
                wick_pct = lower_wick_pct if side == StopHuntSide.BUY else upper_wick_pct
                score = (wick_pct / 100.0) * 0.7 + (penetration_pct / 100.0) * 0.3
                confidence = max(0.0, min(1.0, round(score, 3)))
                explanation = f"Detected {side.value} stop-hunt with wick {wick_pct:.1f}% and penetration {penetration_pct:.1f}%"
                results.append(
                    StopHuntResult(found=True, side=side, confidence=confidence, wick_pct=round(wick_pct, 2), penetration_pct=round(penetration_pct, 2), explanation=explanation)
                )
                logger.debug(explanation)
            else:
                results.append(
                    StopHuntResult(found=False, side=None, confidence=0.0, wick_pct=round(max(upper_wick_pct, lower_wick_pct), 2), penetration_pct=round(penetration_pct, 2), explanation="No stop-hunt detected")
                )

        return results
