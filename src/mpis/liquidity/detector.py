"""Liquidity sweep detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.config import LiquiditySweepConfig


class LiquiditySweepDirection(str, Enum):
    """Direction of a detected liquidity sweep."""

    BUY_SIDE = "buy_side"
    SELL_SIDE = "sell_side"


@dataclass(frozen=True)
class LiquiditySweepResult:
    """Result of liquidity sweep detection."""

    direction: LiquiditySweepDirection
    confidence: float
    swept_price: float
    confirmation_price: float
    timestamp: object
    explanation: str


class LiquiditySweepDetector:
    """Detect buy-side and sell-side liquidity sweeps from OHLC candles."""

    def __init__(self, config: LiquiditySweepConfig | None = None) -> None:
        self.config = config or LiquiditySweepConfig()

    def detect(self, candles: Sequence[Candle]) -> list[LiquiditySweepResult]:
        """Return liquidity sweep signals from the provided candle sequence."""
        if len(candles) < self.config.lookback + 1 + self.config.confirmation_candles:
            return []

        results: list[LiquiditySweepResult] = []
        for index in range(self.config.lookback, len(candles) - self.config.confirmation_candles):
            reference_window = candles[index - self.config.lookback:index]
            if not reference_window:
                continue

            prior_high = max(item.high for item in reference_window)
            prior_low = min(item.low for item in reference_window)
            confirmation_candle = candles[index + self.config.confirmation_candles]

            if self._is_buy_side_sweep(confirmation_candle, prior_high, prior_low):
                results.append(
                    LiquiditySweepResult(
                        direction=LiquiditySweepDirection.BUY_SIDE,
                        confidence=self._confidence(confirmation_candle, prior_high, prior_low, buy_side=True),
                        swept_price=prior_high,
                        confirmation_price=confirmation_candle.close if self.config.require_close_confirmation else confirmation_candle.high,
                        timestamp=confirmation_candle.timestamp,
                        explanation="Buy-side liquidity sweep above the recent swing high.",
                    )
                )
            elif self._is_sell_side_sweep(confirmation_candle, prior_low, prior_high):
                results.append(
                    LiquiditySweepResult(
                        direction=LiquiditySweepDirection.SELL_SIDE,
                        confidence=self._confidence(confirmation_candle, prior_high, prior_low, buy_side=False),
                        swept_price=prior_low,
                        confirmation_price=confirmation_candle.close if self.config.require_close_confirmation else confirmation_candle.low,
                        timestamp=confirmation_candle.timestamp,
                        explanation="Sell-side liquidity sweep below the recent swing low.",
                    )
                )

        return results

    def _is_buy_side_sweep(self, candle: Candle, prior_high: float, prior_low: float) -> bool:
        distance = candle.high - prior_high
        if distance < self.config.minimum_sweep_distance:
            return False
        if self.config.require_wick_confirmation and candle.low >= prior_high:
            return False
        if self.config.require_close_confirmation:
            return candle.close > prior_high
        return candle.high > prior_high

    def _is_sell_side_sweep(self, candle: Candle, prior_low: float, prior_high: float) -> bool:
        distance = prior_low - candle.low
        if distance < self.config.minimum_sweep_distance:
            return False
        if self.config.require_wick_confirmation and candle.high <= prior_low:
            return False
        if self.config.require_close_confirmation:
            return candle.close < prior_low
        return candle.low < prior_low

    @staticmethod
    def _confidence(candle: Candle, prior_high: float, prior_low: float, *, buy_side: bool) -> float:
        if buy_side:
            distance = candle.high - prior_high
            return min(1.0, 0.8 + min(distance / 10.0, 0.2))
        distance = prior_low - candle.low
        return min(1.0, 0.8 + min(distance / 10.0, 0.2))
