"""Replay session management for MPIS."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from mpis.replay.clock import ReplayClock
from mpis.replay.models import ReplayStatus
from mpis.replay.state import ReplayState


@dataclass
class ReplaySession:
    """Domain model representing a replay session."""

    session_id: str
    market: str
    symbol: str
    timeframe: str
    dataset_path: str
    started_at: datetime
    clock: ReplayClock = field(default_factory=ReplayClock)
    ended_at: datetime | None = None
    status: ReplayStatus = ReplayStatus.CREATED
    processed_candles: int = 0

    @property
    def state(self) -> ReplayState:
        """Return an immutable snapshot of current replay state."""
        return ReplayState(
            running=self.clock.is_running,
            paused=self.clock.is_paused,
            finished=self.status == ReplayStatus.FINISHED,
            current_index=self.clock.current_index,
            current_timestamp=self.clock.current_time,
            processed_candles=self.processed_candles,
            remaining_candles=0,
            speed=float(self.clock.speed),
            session_id=self.session_id,
            created_at=self.started_at,
        )

    def start(self) -> None:
        """Start the replay session."""
        if self.status != ReplayStatus.CREATED:
            raise ValueError("Replay session can only start from created state")
        self.status = ReplayStatus.RUNNING

    def pause(self) -> None:
        """Pause the replay session."""
        if self.status != ReplayStatus.RUNNING:
            raise ValueError("Replay session can only pause from running state")
        self.status = ReplayStatus.PAUSED

    def resume(self) -> None:
        """Resume the replay session."""
        if self.status != ReplayStatus.PAUSED:
            raise ValueError("Replay session can only resume from paused state")
        self.status = ReplayStatus.RUNNING

    def finish(self) -> None:
        """Finish the replay session."""
        if self.status == ReplayStatus.FINISHED:
            raise ValueError("Replay session already finished")
        self.status = ReplayStatus.FINISHED
        self.ended_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the replay session."""
        self.status = ReplayStatus.STOPPED
        self.ended_at = datetime.utcnow()
