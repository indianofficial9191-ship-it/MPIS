"""Liquidity grab detection for MPIS psychology sprint 5B."""
from __future__ import annotations

from typing import Sequence

from mpis.data.candle import Candle
from mpis.psychology.models import (
    LiquidityGrabConfig,
    LiquidityGrabDirection,
    LiquidityGrabResult,
)


class LiquidityGrabDetector:
    """Detect liquidity grab events that sweep and reject into a range."""

    def __init__(self, config: LiquidityGrabConfig | None = None) -> None:
        self.config = config or LiquidityGrabConfig()

    def detect(self, candles: Sequence[Candle]) -> list[LiquidityGrabResult]:
        """Return liquidity grab signals from the provided candles."""
        if len(candles) < 2:
            return []

        sorted_candles = sorted(candles, key=lambda candle: candle.timestamp)
        current = sorted_candles[-1]
        prior_range = sorted_candles[:-1]
        prior_high = max(candle.high for candle in prior_range)
        prior_low = min(candle.low for candle in prior_range)
        range_size = current.range if current.range > 0 else 1.0
        body = abs(current.close - current.open)
        upper_wick = current.high - max(current.open, current.close)
        lower_wick = min(current.open, current.close) - current.low

        if current.high > prior_high and current.close < prior_high:
            confidence = min(
                1.0,
                0.3 + (body / range_size) * 0.25 + (upper_wick / range_size) * 0.45,
            )
            return [
                LiquidityGrabResult(
                    found=True,
                    direction=LiquidityGrabDirection.BULLISH,
                    confidence=round(confidence, 3),
                    sweep_price=current.high,
                    rejection_price=current.close,
                    close_back_inside=True,
                    explanation="Bullish liquidity sweep above prior highs followed by a close back inside the range.",
                )
            ]

        if current.low < prior_low and current.close > prior_low:
            confidence = min(
                1.0,
                0.3 + (body / range_size) * 0.25 + (lower_wick / range_size) * 0.45,
            )
            return [
                LiquidityGrabResult(
                    found=True,
                    direction=LiquidityGrabDirection.BEARISH,
                    confidence=round(confidence, 3),
                    sweep_price=current.low,
                    rejection_price=current.close,
                    close_back_inside=True,
                    explanation="Bearish liquidity sweep below prior lows followed by a close back inside the range.",
                )
            ]

        return [
            LiquidityGrabResult(
                found=False,
                direction=LiquidityGrabDirection.NONE,
                confidence=0.0,
                sweep_price=None,
                rejection_price=None,
                close_back_inside=False,
                explanation="No liquidity grab detected.",
            )
        ]
