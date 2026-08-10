"""Sprint 9 unified MPIS signal models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class SignalInput:
    name: str
    side: str
    confidence: float
    weight: float = 1.0
    risk_flag: bool = False
    trap_flag: bool = False


@dataclass(frozen=True)
class UnifiedSignal:
    side: SignalSide
    confidence: float
    quality: str
    direction_bias: str
    trap_warning: bool
    risk_score: float
    alignment_score: float
    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()