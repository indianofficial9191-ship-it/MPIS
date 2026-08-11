"""Sprint 20 live integration models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LiveIntegrationResult:
    symbol: str
    action: str
    confidence: float
    blocked: bool
    reason: str
    timestamp: datetime | None = None
