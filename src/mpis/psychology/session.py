"""Indian market session detection for MPIS psychology."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import Enum


class SessionType(str, Enum):
    """Indian market session labels."""

    PRE_OPEN = "Pre Open"
    OPEN = "Open"
    MORNING = "Morning"
    MID_SESSION = "Mid Session"
    LUNCH = "Lunch"
    POWER_HOUR = "Power Hour"
    CLOSING_SESSION = "Closing Session"
    CLOSED = "Closed"


@dataclass(frozen=True)
class SessionResult:
    """Result of session detection."""

    current_session: SessionType
    remaining_session_time: timedelta


class SessionAnalyzer:
    """Detect current Indian market session and remaining time."""

    SESSIONS: tuple[tuple[SessionType, time, time], ...] = (
        (SessionType.PRE_OPEN, time(9, 0), time(9, 15)),
        (SessionType.OPEN, time(9, 15), time(10, 15)),
        (SessionType.MORNING, time(10, 15), time(12, 0)),
        (SessionType.MID_SESSION, time(12, 0), time(13, 30)),
        (SessionType.LUNCH, time(13, 30), time(14, 15)),
        (SessionType.POWER_HOUR, time(14, 15), time(15, 0)),
        (SessionType.CLOSING_SESSION, time(15, 0), time(15, 30)),
    )

    def get_session(self, timestamp: datetime | None = None) -> SessionResult:
        """Return the current session and remaining session time."""
        timestamp = timestamp or datetime.now()
        current_time = timestamp.time()

        for session, start_time, end_time in self.SESSIONS:
            if start_time <= current_time < end_time:
                remaining = datetime.combine(timestamp.date(), end_time) - timestamp
                return SessionResult(current_session=session, remaining_session_time=remaining)

        if current_time >= self.SESSIONS[-1][2]:
            return SessionResult(current_session=SessionType.CLOSED, remaining_session_time=timedelta(0))

        if current_time < self.SESSIONS[0][1]:
            remaining = datetime.combine(timestamp.date(), self.SESSIONS[0][1]) - timestamp
            return SessionResult(current_session=SessionType.PRE_OPEN, remaining_session_time=remaining)

        return SessionResult(current_session=SessionType.CLOSED, remaining_session_time=timedelta(0))
