"""Sprint 8 final decision models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DecisionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class DecisionEvidence:
    name: str
    side: str
    confidence: float
    weight: float = 1.0
    risk_flag: bool = False


@dataclass(frozen=True)
class DecisionResult:
    side: DecisionSide
    confidence: float
    bullish_score: float
    bearish_score: float
    conflict_score: float
    risk_score: float
    signal_quality: str
    contributors: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()