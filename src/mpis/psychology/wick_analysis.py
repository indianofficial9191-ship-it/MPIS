"""Wick analysis for MPIS psychology sprint 5B."""
from __future__ import annotations

from mpis.data.candle import Candle
from mpis.psychology.models import (
    WickAnalysisClassification,
    WickAnalysisResult,
)


class WickAnalyzer:
    """Analyze candle wick composition for rejection signals."""

    def analyze(self, candle: Candle) -> WickAnalysisResult:
        """Return wick percentage composition and rejection classification."""
        range_size = candle.range if candle.range > 0 else 1.0
        upper_wick_pct = (candle.upper_wick / range_size) * 100.0
        lower_wick_pct = (candle.lower_wick / range_size) * 100.0
        body_pct = (abs(candle.close - candle.open) / range_size) * 100.0

        if (
            upper_wick_pct >= lower_wick_pct
            and upper_wick_pct >= 40.0
            and candle.close < candle.open
        ):
            classification = WickAnalysisClassification.BEARISH_REJECTION
        elif (
            lower_wick_pct > upper_wick_pct
            and lower_wick_pct >= 40.0
            and candle.close > candle.open
        ):
            classification = WickAnalysisClassification.BULLISH_REJECTION
        else:
            classification = WickAnalysisClassification.NEUTRAL

        return WickAnalysisResult(
            upper_wick_pct=round(upper_wick_pct, 2),
            lower_wick_pct=round(lower_wick_pct, 2),
            body_pct=round(body_pct, 2),
            classification=classification,
        )
