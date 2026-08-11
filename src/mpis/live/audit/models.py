"""Sprint 22 live decision audit models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AuditDecision(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class AuditEvent:
    symbol: str
    action: AuditDecision
    confidence: float
    accepted: bool
    reason: str
    timestamp: datetime
    source: str

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("Symbol must not be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        if not self.reason.strip():
            raise ValueError("Reason must not be empty")

        if not self.source.strip():
            raise ValueError("Source must not be empty")
