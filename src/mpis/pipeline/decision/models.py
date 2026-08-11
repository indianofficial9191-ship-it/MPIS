"""Models for the Sprint 10 pipeline decision layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PipelineDecisionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class PipelineDecisionInput:
    """Normalized output from an upstream MPIS layer."""

    name: str
    side: str
    confidence: float
    weight: float = 1.0
    risk_flag: bool = False
    trap_flag: bool = False


@dataclass(frozen=True)
class PipelineDecisionResult:
    """Final pipeline-level MPIS decision."""

    side: PipelineDecisionSide
    confidence: float
    direction_bias: str
    alignment_score: float
    risk_score: float
    trap_warning: bool
    quality: str
    contributors: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()