"""Sprint 11 live signal models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LiveSignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class LiveSignalInput:
    """Normalized signal received from the live MPIS pipeline."""

    name: str
    side: str
    confidence: float
    weight: float = 1.0
    stale: bool = False
    risk_flag: bool = False


@dataclass(frozen=True)
class LiveSignalResult:
    """Validated live signal decision."""

    side: LiveSignalSide
    confidence: float
    direction_bias: str
    quality: str
    stale_warning: bool
    risk_score: float
    alignment_score: float
    contributors: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()