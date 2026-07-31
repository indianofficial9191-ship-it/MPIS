"""Institutional market classification for MPIS."""
from __future__ import annotations

from mpis.institutional.models import ConfidenceLevel, MarketState


class InstitutionalClassifier:
    """Classifier for market state and confidence."""

    @staticmethod
    def classify_market_state(bullish_score: float, bearish_score: float) -> MarketState:
        """Classify market state from bullish and bearish psychology scores."""
        delta = bullish_score - bearish_score
        if delta >= 50:
            return MarketState.STRONG_BULLISH
        if delta >= 20:
            return MarketState.BULLISH
        if delta >= 5:
            return MarketState.SLIGHT_BULLISH
        if delta <= -50:
            return MarketState.STRONG_BEARISH
        if delta <= -20:
            return MarketState.BEARISH
        if delta <= -5:
            return MarketState.SLIGHT_BEARISH
        return MarketState.NEUTRAL

    @staticmethod
    def classify_confidence(score: float) -> ConfidenceLevel:
        """Classify the confidence level from a numeric score."""
        if score >= 85.0:
            return ConfidenceLevel.VERY_HIGH
        if score >= 70.0:
            return ConfidenceLevel.HIGH
        if score >= 50.0:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
