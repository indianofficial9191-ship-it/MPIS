"""Opening range analysis for MPIS psychology."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Sequence

from mpis.data.candle import Candle
from mpis.psychology.models import (
    OpeningRangeAnalysisResult,
    OpeningRangeDirection,
)


VALID_RANGE_MINUTES = {5, 15, 30}


@dataclass(frozen=True)
class OpeningRangeAnalyzer:
    """Analyze opening range structure and breakout behavior."""

    range_minutes: int = 15

    def analyze(self, candles: Sequence[Candle]) -> OpeningRangeAnalysisResult:
        """Return opening range details for a list of candles."""
        if self.range_minutes not in VALID_RANGE_MINUTES:
            raise ValueError(
                f"range_minutes must be one of {sorted(VALID_RANGE_MINUTES)}"
            )
        if not candles:
            raise ValueError("candles must contain at least one candle")

        sorted_candles = sorted(candles, key=lambda candle: candle.timestamp)
        window_start = sorted_candles[0].timestamp
        window_end = window_start + timedelta(minutes=self.range_minutes)
        opening_range_candles = [
            candle for candle in sorted_candles if candle.timestamp < window_end
        ]

        opening_range_high = max(candle.high for candle in opening_range_candles)
        opening_range_low = min(candle.low for candle in opening_range_candles)
        range_size = opening_range_high - opening_range_low

        later_candles = [
            candle for candle in sorted_candles if candle.timestamp >= window_end
        ]
        breakout = False
        breakout_direction = OpeningRangeDirection.NONE
        fake_breakout = False
        retest = False

        if later_candles:
            breakout_index = None
            for index, candle in enumerate(later_candles):
                if candle.close > opening_range_high:
                    breakout = True
                    breakout_direction = OpeningRangeDirection.UP
                    breakout_index = index
                    break
                if candle.close < opening_range_low:
                    breakout = True
                    breakout_direction = OpeningRangeDirection.DOWN
                    breakout_index = index
                    break

            if breakout and breakout_index is not None:
                following_candles = later_candles[breakout_index + 1 :]
                for candle in following_candles:
                    if breakout_direction == OpeningRangeDirection.UP:
                        if candle.low <= opening_range_high:
                            retest = True
                        if opening_range_low <= candle.close <= opening_range_high:
                            fake_breakout = True
                    elif breakout_direction == OpeningRangeDirection.DOWN:
                        if candle.high >= opening_range_low:
                            retest = True
                        if opening_range_low <= candle.close <= opening_range_high:
                            fake_breakout = True
                    if retest and fake_breakout:
                        break
                if following_candles and not fake_breakout:
                    first_candle = following_candles[0]
                    if opening_range_low <= first_candle.close <= opening_range_high:
                        fake_breakout = True

        return OpeningRangeAnalysisResult(
            range_minutes=self.range_minutes,
            opening_range_high=opening_range_high,
            opening_range_low=opening_range_low,
            range_size=range_size,
            breakout=breakout,
            breakout_direction=breakout_direction,
            fake_breakout=fake_breakout,
            retest=retest,
        )
