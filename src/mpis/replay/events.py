"""Replay event models for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReplayEvent:
    """Base event for replay lifecycle notifications."""

    session_id: str
    timestamp: datetime
    index: int
    event_time: datetime


@dataclass(frozen=True)
class ReplayStartedEvent(ReplayEvent):
    """Event emitted when replay begins."""


@dataclass(frozen=True)
class ReplayPausedEvent(ReplayEvent):
    """Event emitted when replay is paused."""


@dataclass(frozen=True)
class ReplayResumedEvent(ReplayEvent):
    """Event emitted when replay resumes."""


@dataclass(frozen=True)
class ReplayStoppedEvent(ReplayEvent):
    """Event emitted when replay stops."""


@dataclass(frozen=True)
class ReplayFinishedEvent(ReplayEvent):
    """Event emitted when replay completes."""


@dataclass(frozen=True)
class ReplayStepEvent(ReplayEvent):
    """Event emitted when replay advances by one candle."""


@dataclass(frozen=True)
class ReplaySeekEvent(ReplayEvent):
    """Event emitted when replay seeks to a new index."""
