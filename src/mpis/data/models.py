"""Data models for MPIS market data foundation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class DataHealthStatus(str, Enum):
    """Health states for the market data subsystem."""

    UNKNOWN = "unknown"
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class CSVLoadResult:
    """Summary metrics from loading a CSV dataset."""

    rows_loaded: int
    duplicate_count: int
    duration_seconds: float
    buffer_size: int
    status: DataHealthStatus
    warnings: Sequence[str] = ()
