"""Replay models for MPIS."""
from __future__ import annotations

from enum import Enum


class ReplayStatus(str, Enum):
    """Status values for replay lifecycle."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"


class ReplaySpeed(float, Enum):
    """Replay speed multipliers."""

    QUARTER = 0.25
    HALF = 0.5
    NORMAL = 1.0
    DOUBLE = 2.0
    QUADRUPLE = 4.0
    OCTUPLE = 8.0
    HEXADECUPLE = 16.0
