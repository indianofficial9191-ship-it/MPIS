"""Sprint 12 live pipeline health models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass(frozen=True)
class HealthInput:
    """Health evidence from one live MPIS component."""

    name: str
    healthy: bool = True
    latency_ms: float = 0.0
    error_rate: float = 0.0
    stale: bool = False
    weight: float = 1.0


@dataclass(frozen=True)
class HealthResult:
    """Aggregated live pipeline health."""

    status: HealthStatus
    health_score: float
    latency_score: float
    error_score: float
    stale_warning: bool
    unhealthy_components: tuple[str, ...] = ()