"""Immutable replay state for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReplayState:
    """Immutable snapshot of replay state."""

    running: bool
    paused: bool
    finished: bool
    current_index: int
    current_timestamp: datetime
    processed_candles: int
    remaining_candles: int
    speed: float
    session_id: str
    created_at: datetime
