"""Probability engine for trade decisions (Sprint 5 Batch 5.6).

Converts a TradeFusionResult into a probabilistic decision, risk categorization,
and trade allowance based on a configurable minimum probability threshold.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from mpis.psychology.fusion import TradeFusionResult, TradeDecision


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ProbabilityResult:
    probability: float  # 0..100
    decision: TradeDecision
    confidence: float  # original fusion confidence 0..100
    risk_level: RiskLevel
    trade_allowed: bool
    reasons: List[str]


class ProbabilityEngine:
    """Engine to convert fusion output into a probability and trade permission.

    The probability is primarily derived from fusion.confidence with a small
    adjustment based on reward vs risk. All outputs are deterministic and
    clamped to the 0..100 range.
    """

    def __init__(self, minimum_trade_probability: float = 50.0) -> None:
        self.minimum_trade_probability = float(minimum_trade_probability)

    def analyze(self, fusion: TradeFusionResult) -> ProbabilityResult:
        reasons: List[str] = []

        # Base probability equals fusion confidence (0..100)
        base = float(fusion.confidence)
        reasons.append(f"Base probability from fusion confidence: {base}")

        # Adjustment: reward vs risk differential scaled down to avoid overfitting
        # adjustment = (reward - risk) * 0.25
        adjustment = (float(fusion.reward_score) - float(fusion.risk_score)) * 0.25
        reasons.append(f"Reward-Risk adjustment: {adjustment} (reward {fusion.reward_score} - risk {fusion.risk_score}) * 0.25")

        probability = base + adjustment

        # Clamp probability to 0..100
        probability = max(0.0, min(100.0, round(probability, 2)))
        reasons.append(f"Clamped probability: {probability}")

        # Risk level from fusion.risk_score
        r = float(fusion.risk_score)
        if r < 33.33:
            risk_level = RiskLevel.LOW
        elif r < 66.66:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        reasons.append(f"Risk level derived from risk_score {r}: {risk_level.value}")

        # Trade allowed if probability >= threshold
        trade_allowed = probability >= float(self.minimum_trade_probability)
        if trade_allowed:
            reasons.append(f"Trade allowed: probability {probability} >= minimum {self.minimum_trade_probability}")
        else:
            reasons.append(f"Trade not allowed: probability {probability} < minimum {self.minimum_trade_probability}")

        return ProbabilityResult(
            probability=probability,
            decision=fusion.decision,
            confidence=fusion.confidence,
            risk_level=risk_level,
            trade_allowed=trade_allowed,
            reasons=reasons,
        )
