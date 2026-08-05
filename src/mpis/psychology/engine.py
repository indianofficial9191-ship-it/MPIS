"""Lightweight PsychologyEngine for probability computation.

This module provides a compact PsychologyEngine focused on computing a
probability and confidence for a directional decision using already-produced
models (TrendContext and PsychologyScore).

The implementation is deterministic and intentionally small: compute_probability
combines trend and psychological score confidences with fixed weights and
returns a small result structure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from mpis.psychology.models import TrendContext
from mpis.psychology.score import PsychologyScore, MarketBias


@dataclass(frozen=True)
class ProbabilityOutput:
    """Returned result from compute_probability.

    Attributes:
        direction: 'buy'|'sell'|'neutral' - suggested trade direction
        confidence: float - composite confidence 0..100
        probability: float - computed probability 0..100
        reasons: List[str] - human-readable explanation list
    """

    direction: str
    confidence: float
    probability: float
    reasons: List[str]


class PsychologyEngine:
    """Simple engine to compute a probability from trend and psychology scores.

    Rules (deterministic):
      - trend confidence (TrendContext.confidence) is 0..1 and scaled to 0..100
      - psychology confidence (PsychologyScore.confidence) is 0..100
      - composite confidence = round(mean(trend_pct, psychology_conf), 2)
      - probability = round(trend_pct * 0.6 + psychology_conf * 0.4, 2)
      - direction: prefer psychology bias if not NEUTRAL, otherwise infer from trend
      - reasons explain source values and weights
    """

    def __init__(self, trend_weight: float = 0.6, psychology_weight: float = 0.4) -> None:
        if not (0.0 <= trend_weight <= 1.0 and 0.0 <= psychology_weight <= 1.0):
            raise ValueError("weights must be between 0 and 1")
        if abs((trend_weight + psychology_weight) - 1.0) > 1e-8:
            raise ValueError("weights must sum to 1.0")
        self.trend_weight = float(trend_weight)
        self.psychology_weight = float(psychology_weight)

    def compute_probability(self, trend: TrendContext | None, psychology: PsychologyScore | None) -> ProbabilityOutput:
        """Compute direction, confidence and probability from inputs.

        Parameters:
            trend: TrendContext or None
            psychology: PsychologyScore or None

        Returns:
            ProbabilityOutput dataclass with direction, confidence, probability and reasons.
        """
        reasons: List[str] = []

        # Extract numerical confidences
        trend_pct = 0.0
        if trend is not None:
            try:
                trend_pct = float(trend.confidence) * 100.0
            except Exception:
                trend_pct = 0.0
            reasons.append(f"Trend confidence (scaled): {round(trend_pct,2)}")
        else:
            reasons.append("No trend context provided; using 0")

        psych_pct = 0.0
        bias_str = "neutral"
        if psychology is not None:
            try:
                psych_pct = float(psychology.confidence)
            except Exception:
                psych_pct = 0.0
            bias = getattr(psychology, "bias", None)
            if isinstance(bias, MarketBias):
                bias_str = bias.value
            else:
                bias_str = str(bias) if bias is not None else "neutral"
            reasons.append(f"Psychology confidence: {round(psych_pct,2)} bias: {bias_str}")
        else:
            reasons.append("No psychology score provided; using 0")

        # Composite confidence and probability
        confidence = round((trend_pct + psych_pct) / 2.0, 2)
        probability = round(trend_pct * self.trend_weight + psych_pct * self.psychology_weight, 2)

        # Clamp
        confidence = max(0.0, min(100.0, confidence))
        probability = max(0.0, min(100.0, probability))

        reasons.append(f"Composite confidence (mean): {confidence}")
        reasons.append(f"Probability = trend*{self.trend_weight} + psychology*{self.psychology_weight} => {probability}")

        # Decide direction
        direction = "neutral"
        if psychology is not None and bias_str and bias_str != MarketBias.NEUTRAL.value:
            # use psychology bias first
            direction = "buy" if "buy" in bias_str else "sell" if "sell" in bias_str else "neutral"
            reasons.append(f"Direction taken from psychology bias: {bias_str}")
        elif trend is not None:
            t = getattr(trend, "trend", None)
            t_str = str(t).lower() if t is not None else "sideways"
            if "very_bull" in t_str or "bull" in t_str:
                direction = "buy"
            elif "very_bear" in t_str or "bear" in t_str:
                direction = "sell"
            else:
                direction = "neutral"
            reasons.append(f"Direction inferred from trend: {t_str}")
        else:
            reasons.append("No direction inputs; returning neutral")

        return ProbabilityOutput(direction=direction, confidence=confidence, probability=probability, reasons=reasons)
