"""Stop-hunt detector for the liquidity engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.models import StopHuntResult


@dataclass(frozen=True)
class StopHuntConfig:
    """Configuration for stop-hunt detection."""

    sweep_threshold: float = 0.5
    rejection_threshold: float = 0.5
    require_close_back: bool = True


class StopHuntDetector:
    """Detect a bullish or bearish stop hunt with sweep and rejection behavior."""

    def __init__(self, config: StopHuntConfig | None = None) -> None:
        self.config = config or StopHuntConfig()

    def detect(self, candles: Sequence[Candle]) -> list[StopHuntResult]:
        """Return stop-hunt signals for the candle sequence."""
        if len(candles) < 3:
            return []

        previous = candles[-2]
        current = candles[-1]
        previous_high = max(item.high for item in candles[:-1])
        previous_low = min(item.low for item in candles[:-1])

        above_move = current.high - previous_high
        below_move = previous_low - current.low

        if above_move >= self.config.sweep_threshold and above_move >= below_move:
            if self.config.require_close_back:
                if current.close <= previous_high:
                    return [
                        StopHuntResult(
                            direction="above_highs",
                            confidence=min(0.99, 0.8 + above_move / 20.0),
                            sweep_price=current.high,
                            rejection_price=current.close,
                            price=current.high,
                            explanation="Price swept above the prior highs and then rejected back inside the range.",
                            timestamp=current.timestamp,
                        )
                    ]
            else:
                return [
                    StopHuntResult(
                        direction="above_highs",
                        confidence=min(0.99, 0.8 + above_move / 20.0),
                        sweep_price=current.high,
                        rejection_price=current.close,
                        price=current.high,
                        explanation="Price swept above the prior highs.",
                        timestamp=current.timestamp,
                    )
                ]

        if below_move >= self.config.sweep_threshold and below_move > above_move:
            if self.config.require_close_back:
                if current.close >= previous_low:
                    return [
                        StopHuntResult(
                            direction="below_lows",
                            confidence=min(0.99, 0.8 + below_move / 20.0),
                            sweep_price=current.low,
                            rejection_price=current.close,
                            price=current.low,
                            explanation="Price swept below the prior lows and then rejected back inside the range.",
                            timestamp=current.timestamp,
                        )
                    ]
            else:
                return [
                    StopHuntResult(
                        direction="below_lows",
                        confidence=min(0.99, 0.8 + below_move / 20.0),
                        sweep_price=current.low,
                        rejection_price=current.close,
                        price=current.low,
                        explanation="Price swept below the prior lows.",
                        timestamp=current.timestamp,
                    )
                ]
        return []
