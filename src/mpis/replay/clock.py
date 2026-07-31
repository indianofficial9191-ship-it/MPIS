"""Replay clock implementation for MPIS."""
from __future__ import annotations

from datetime import datetime, timedelta

from mpis.core.exceptions import ReplayError
from mpis.replay.models import ReplaySpeed


class ReplayClock:
    """Clock representing replay position and timing."""

    def __init__(self, speed: ReplaySpeed = ReplaySpeed.NORMAL, start_time: datetime | None = None) -> None:
        self._speed = speed
        self._current_index = 0
        self._current_time = start_time or datetime.utcnow()
        self._running = False
        self._paused = False
        self._start_time = self._current_time

    @property
    def current_time(self) -> datetime:
        """Return the current replay timestamp."""
        return self._current_time

    @property
    def current_index(self) -> int:
        """Return the current replay index."""
        return self._current_index

    @property
    def speed(self) -> ReplaySpeed:
        """Return the configured replay speed."""
        return self._speed

    @speed.setter
    def speed(self, value: ReplaySpeed) -> None:
        if value not in set(ReplaySpeed):
            raise ReplayError(f"Invalid replay speed: {value}")
        self._speed = value

    @property
    def is_running(self) -> bool:
        """Return True when replay is currently running."""
        return self._running and not self._paused

    @property
    def is_paused(self) -> bool:
        """Return True when replay is paused."""
        return self._paused

    def start(self) -> None:
        """Start the replay clock."""
        if self._running and not self._paused:
            raise ReplayError("Replay clock is already running")
        self._running = True
        self._paused = False
        self._current_time = self._current_time or datetime.utcnow()

    def pause(self) -> None:
        """Pause the replay clock."""
        if not self._running or self._paused:
            raise ReplayError("Replay clock must be running to pause")
        self._paused = True

    def resume(self) -> None:
        """Resume the replay clock."""
        if not self._paused:
            raise ReplayError("Replay clock must be paused to resume")
        self._paused = False
        self._running = True

    def stop(self) -> None:
        """Stop the replay clock."""
        self._running = False
        self._paused = False

    def seek(self, index: int) -> None:
        """Seek the clock to a specific index."""
        if index < 0:
            raise ReplayError("Seek index must not be negative")
        self._current_index = index
        self._current_time = self._start_time + self._time_delta_for_index(index)

    def step(self) -> None:
        """Advance the replay clock by one step."""
        if not self._running and not self._paused:
            raise ReplayError("Replay clock must be started before stepping")
        self._current_index += 1
        self._current_time += self._step_delta()

    def reset(self) -> None:
        """Reset the replay clock to its initial state."""
        self._current_index = 0
        self._current_time = self._start_time
        self._running = False
        self._paused = False

    def _step_delta(self) -> timedelta:
        return timedelta(seconds=float(self._speed))

    def _time_delta_for_index(self, index: int) -> timedelta:
        return timedelta(seconds=float(self._speed) * index)
