"""Models for the Sprint 7 institutional confirmation engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConfirmationSide(str, Enum):
    """Final directional confirmation."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class ConfirmationInput:
    """Normalized directional evidence from one upstream engine."""

    name: str
    side: str
    score: float = 0.0
    weight: float = 1.0


@dataclass(frozen=True)
class ConfirmationResult:
    """Final Sprint 7 confirmation decision."""

    side: ConfirmationSide
    confidence: float
    alignment_score: float
    bullish_score: float
    bearish_score: float
    conflict_score: float
    contributors: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()