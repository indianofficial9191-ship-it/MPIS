"""Fake breakout detection for MPIS psychology sprint 5B."""
from __future__ import annotations

from typing import Sequence

from mpis.data.candle import Candle
from mpis.psychology.models import (
    FakeBreakoutConfig,
    FakeBreakoutResult,
    FakeBreakoutType,
)


class FakeBreakoutDetector:
    """Detect false breakout patterns using price confirmation behavior."""

    def __init__(self, config: FakeBreakoutConfig | None = None) -> None:
        self.config = config or FakeBreakoutConfig()

    def detect(
        self,
        candles: Sequence[Candle],
        opening_range_high: float | None = None,
        opening_range_low: float | None = None,
        previous_day_high: float | None = None,
        previous_day_low: float | None = None,
    ) -> list[FakeBreakoutResult]:
        """Return fake breakout signals for the provided candle sequence."""
        if len(candles) < self.config.confirmation_candles + 2:
            return []

        sorted_candles = sorted(candles, key=lambda candle: candle.timestamp)
        signals: list[FakeBreakoutResult] = []

        def add_signal(
            breakout_type: FakeBreakoutType,
            direction: str,
            trigger_price: float,
            close_price: float,
            timestamp: object,
            explanation: str,
        ) -> None:
            signals.append(
                FakeBreakoutResult(
                    breakout_type=breakout_type,
                    direction=direction,
                    confidence=0.75,
                    trigger_price=trigger_price,
                    close_price=close_price,
                    timestamp=timestamp,
                    explanation=explanation,
                )
            )

        # Anchor-based false breakout checks.
        self._detect_anchor_false_breakout(
            sorted_candles,
            opening_range_high,
            FakeBreakoutType.FALSE_OPENING_RANGE,
            signals,
            direction="up",
        )
        self._detect_anchor_false_breakout(
            sorted_candles,
            opening_range_low,
            FakeBreakoutType.FALSE_OPENING_RANGE,
            signals,
            direction="down",
        )
        self._detect_anchor_false_breakout(
            sorted_candles,
            previous_day_high,
            FakeBreakoutType.FALSE_PDH_BREAK,
            signals,
            direction="up",
        )
        self._detect_anchor_false_breakout(
            sorted_candles,
            previous_day_low,
            FakeBreakoutType.FALSE_PDL_BREAK,
            signals,
            direction="down",
        )

        # General structure false breakouts.
        for index in range(1, len(sorted_candles) - self.config.confirmation_candles):
            candidate = sorted_candles[index]
            prior_candles = sorted_candles[:index]
            if not prior_candles:
                continue

            prior_high = max(candle.high for candle in prior_candles)
            prior_low = min(candle.low for candle in prior_candles)
            confirmation_candles = sorted_candles[index + 1 : index + 1 + self.config.confirmation_candles]

            if candidate.close > prior_high and any(c.close <= prior_high for c in confirmation_candles):
                breakout_type = self._infer_false_breakout_type(prior_candles, direction="up")
                add_signal(
                    breakout_type=breakout_type,
                    direction="up",
                    trigger_price=candidate.close,
                    close_price=confirmation_candles[-1].close,
                    timestamp=confirmation_candles[-1].timestamp,
                    explanation="Price broke above prior resistance and failed to hold in follow-through candles.",
                )
                break

            if candidate.close < prior_low and any(c.close >= prior_low for c in confirmation_candles):
                breakout_type = self._infer_false_breakout_type(prior_candles, direction="down")
                add_signal(
                    breakout_type=breakout_type,
                    direction="down",
                    trigger_price=candidate.close,
                    close_price=confirmation_candles[-1].close,
                    timestamp=confirmation_candles[-1].timestamp,
                    explanation="Price broke below prior support and then reversed back inside the prior range.",
                )
                break

        return signals

    def _detect_anchor_false_breakout(
        self,
        candles: Sequence[Candle],
        anchor_price: float | None,
        breakout_type: FakeBreakoutType,
        signals: list[FakeBreakoutResult],
        direction: str,
    ) -> None:
        if anchor_price is None:
            return

        for index, candle in enumerate(candles[:-self.config.confirmation_candles]):
            if direction == "up" and candle.close > anchor_price:
                confirmation = candles[index + 1 : index + 1 + self.config.confirmation_candles]
                if any(confirmation_candle.close <= anchor_price for confirmation_candle in confirmation):
                    signals.append(
                        FakeBreakoutResult(
                            breakout_type=breakout_type,
                            direction=direction,
                            confidence=0.8,
                            trigger_price=candle.close,
                            close_price=confirmation[-1].close,
                            timestamp=confirmation[-1].timestamp,
                            explanation=f"Price broke above anchor {anchor_price} and then closed back below it.",
                        )
                    )
                    return
            if direction == "down" and candle.close < anchor_price:
                confirmation = candles[index + 1 : index + 1 + self.config.confirmation_candles]
                if any(confirmation_candle.close >= anchor_price for confirmation_candle in confirmation):
                    signals.append(
                        FakeBreakoutResult(
                            breakout_type=breakout_type,
                            direction=direction,
                            confidence=0.8,
                            trigger_price=candle.close,
                            close_price=confirmation[-1].close,
                            timestamp=confirmation[-1].timestamp,
                            explanation=f"Price broke below anchor {anchor_price} and then reverted back above it.",
                        )
                    )
                    return

    def _infer_false_breakout_type(
        self,
        prior_candles: Sequence[Candle],
        direction: str,
    ) -> FakeBreakoutType:
        if len(prior_candles) < 3:
            return FakeBreakoutType.FALSE_BOS

        last = prior_candles[-1]
        prior = prior_candles[-2]
        if direction == "up" and last.low > prior.low and last.high > prior.high:
            return FakeBreakoutType.FALSE_CHOCH
        if direction == "down" and last.high < prior.high and last.low < prior.low:
            return FakeBreakoutType.FALSE_CHOCH
        return FakeBreakoutType.FALSE_BOS
