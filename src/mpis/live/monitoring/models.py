"""Sprint 13 live monitoring models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MonitoringStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class MonitoringInput:
    name: str
    active: bool = True
    age_seconds: float = 0.0
    latency_ms: float = 0.0
    error_rate: float = 0.0


@dataclass(frozen=True)
class MonitoringResult:
    status: MonitoringStatus
    health_score: float
    stale_sources: tuple[str, ...] = ()
    latency_sources: tuple[str, ...] = ()
    error_sources: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
