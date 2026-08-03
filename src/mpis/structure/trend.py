"""Trend detection for MPIS market structure analysis."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mpis.structure.models import TrendState, StructureSignal


@dataclass(frozen=True)
class TrendAnalysis:
    """A trend analysis result describing current market direction."""

    trend: TrendState
    higher_high: bool
    higher_low: bool
    lower_high: bool
    lower_low: bool


class TrendDetector:
    """Detect market trend state from swing structure."""

    def detect(self, swings: Sequence[StructureSignal]) -> TrendAnalysis:
        """Detect the market trend from swing signals."""
        if len(swings) < 2:
            return TrendAnalysis(
                trend=TrendState.RANGE,
                higher_high=False,
                higher_low=False,
                lower_high=False,
                lower_low=False,
            )

        last = swings[-1]
        previous = swings[-2]

        higher_high = last.price > previous.price and last.direction == previous.direction == TrendState.UPTREND
        higher_low = last.price > previous.price and last.direction == previous.direction == TrendState.UPTREND
        lower_high = last.price < previous.price and last.direction == previous.direction == TrendState.DOWNTREND
        lower_low = last.price < previous.price and last.direction == previous.direction == TrendState.DOWNTREND

        if higher_high and higher_low:
            trend = TrendState.UPTREND
        elif lower_high and lower_low:
            trend = TrendState.DOWNTREND
        else:
            trend = TrendState.RANGE

        return TrendAnalysis(
            trend=trend,
            higher_high=higher_high,
            higher_low=higher_low,
            lower_high=lower_high,
            lower_low=lower_low,
        )
