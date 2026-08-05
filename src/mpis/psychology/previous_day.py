"""Previous-day analysis for MPIS psychology."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Sequence

from mpis.data.candle import Candle
from mpis.psychology.models import GapDirection, PreviousDayAnalysisResult


@dataclass(frozen=True)
class PreviousDayAnalyzer:
    """Analyze previous trading day price structure and gaps."""

    def analyze(
        self,
        previous_day_candles: Sequence[Candle],
        current_day_candles: Sequence[Candle] | None = None,
    ) -> PreviousDayAnalysisResult:
        """Return previous day analysis and gap details."""
        if not previous_day_candles:
            raise ValueError("previous_day_candles must contain at least one candle")

        current_day_candles = current_day_candles or []
        sorted_previous = sorted(previous_day_candles, key=lambda candle: candle.timestamp)
        previous_high = max(candle.high for candle in sorted_previous)
        previous_low = min(candle.low for candle in sorted_previous)
        previous_close = sorted_previous[-1].close

        if current_day_candles:
            sorted_current = sorted(current_day_candles, key=lambda candle: candle.timestamp)
            current_open = sorted_current[0].open
            gap_amount = current_open - previous_close
            gap_percent = 0.0 if previous_close == 0 else (gap_amount / previous_close) * 100.0
            if current_open > previous_close:
                gap_direction = GapDirection.UP
            elif current_open < previous_close:
                gap_direction = GapDirection.DOWN
            else:
                gap_direction = GapDirection.NONE
            gap_filled = any(
                candle.low <= previous_close <= candle.high for candle in sorted_current
            )
        else:
            current_open = None
            gap_amount = 0.0
            gap_percent = 0.0
            gap_direction = GapDirection.NONE
            gap_filled = False

        return PreviousDayAnalysisResult(
            previous_high=previous_high,
            previous_low=previous_low,
            previous_close=previous_close,
            current_open=current_open,
            gap_amount=gap_amount,
            gap_percent=round(gap_percent, 4),
            gap_direction=gap_direction,
            gap_filled=gap_filled,
        )
