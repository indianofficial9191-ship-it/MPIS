"""Specialized models for option open interest analysis in MPIS."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParticipantOIState:
    """Derived open interest state for a participant."""

    participant_name: str
    participant_type: str
    net_oi: float
    long_change: float
    short_change: float
    position_type: str
    conviction: float
