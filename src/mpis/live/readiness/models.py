"""Sprint 14 live decision readiness models."""

from dataclasses import dataclass
from enum import Enum


class ReadinessStatus(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"


@dataclass(frozen=True)
class ReadinessInput:
    name: str
    healthy: bool = True
    confidence: float = 1.0
    risk_flag: bool = False


@dataclass(frozen=True)
class ReadinessResult:
    status: ReadinessStatus
    readiness_score: float
    confidence: float
    blocked_reasons: tuple[str, ...] = ()
    degraded_reasons: tuple[str, ...] = ()
