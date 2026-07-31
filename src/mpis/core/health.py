"""Health monitoring utilities for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class HealthStatus(str, Enum):
    """Enumerated health states for core monitor."""

    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthMonitor:
    """Maintains health state and details for a component."""

    status: HealthStatus = HealthStatus.OK
    details: dict[str, str] = None

    def __post_init__(self) -> None:
        if self.details is None:
            self.details = {}

    def report(self, status: HealthStatus, details: Mapping[str, str] | None = None) -> None:
        """Report a new health status and optional details."""
        self.status = status
        if details is not None:
            self.details = dict(details)

    def add_detail(self, key: str, value: str) -> None:
        """Add or update a health detail entry."""
        self.details[key] = value

    def clear_details(self) -> None:
        """Remove all health details."""
        self.details.clear()

    def is_healthy(self) -> bool:
        """Return True when status is OK."""
        return self.status == HealthStatus.OK

    def summary(self) -> dict[str, str | HealthStatus]:
        """Return a summary of status and details."""
        return {"status": self.status, "details": dict(self.details)}
