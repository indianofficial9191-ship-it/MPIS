"""Sprint 15 live execution guard models."""

from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ExecutionInput:
    name: str
    ready: bool = True
    confidence: float = 1.0
    risk_score: float = 0.0
    trap_warning: bool = False


@dataclass(frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    execution_score: float
    reasons: tuple[str, ...] = ()
