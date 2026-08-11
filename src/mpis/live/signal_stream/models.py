"""Sprint 18 live signal stream models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SignalAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class SignalEvent:
    signal_id: str
    symbol: str
    action: SignalAction
    confidence: float
    timestamp: datetime
    source: str = "mpis"


@dataclass(frozen=True)
class SignalStreamSnapshot:
    symbol: str
    latest: SignalEvent | None
    event_count: int
    sequence: int