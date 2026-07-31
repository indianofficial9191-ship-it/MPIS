"""Replay execution engine for MPIS."""
from __future__ import annotations

from datetime import datetime
from typing import Iterator

from mpis.core.exceptions import ReplayError
from mpis.core.health import HealthMonitor, HealthStatus
from mpis.core.timer import Timer
from mpis.data.buffer import ReplayBuffer
from mpis.utils.logger import get_logger
from mpis.utils.logger import log_replay_event

from .callbacks import ReplayCallbackRegistry
from .clock import ReplayClock
from .events import (
    ReplayFinishedEvent,
    ReplayPausedEvent,
    ReplayResumedEvent,
    ReplaySeekEvent,
    ReplayStartedEvent,
    ReplayStepEvent,
    ReplayStoppedEvent,
)
from .models import ReplaySpeed, ReplayStatus
from .state import ReplayState
from .session import ReplaySession


class ReplayEngine:
    """Engine that manages replay execution state and orchestration."""

    def __init__(self, session: ReplaySession, buffer: ReplayBuffer, clock: "ReplayClock") -> None:
        self.session = session
        self.buffer = buffer
        self.clock = clock
        self.logger = get_logger("mpis.replay.engine")
        self.health = HealthMonitor()
        self.callbacks = ReplayCallbackRegistry()

    def initialize(self) -> None:
        """Initialize the replay engine and validate initial state."""
        self.session.status = ReplayStatus.CREATED
        self.health.report(
            HealthStatus.OK,
            {"message": "replay engine initialized"},
        )
        self.logger.info("Replay engine initialized", extra={"session_id": self.session.session_id})

    def load_buffer(self, buffer: ReplayBuffer) -> None:
        """Load the replay buffer into the engine."""
        self.buffer = buffer
        self.clock.reset()
        self.session.status = ReplayStatus.CREATED
        self.logger.info("Replay buffer loaded", extra={"session_id": self.session.session_id, "buffer_size": len(self.buffer)})

    def start(self) -> None:
        """Start replay execution."""
        if self.session.status != ReplayStatus.CREATED:
            raise ReplayError("Replay can only start from created state")
        self.clock.start()
        self.session.start()
        self.health.report(
            HealthStatus.OK,
            {"message": "replay started"},
        )
        self._dispatch_event(ReplayStartedEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
        log_replay_event(self.logger, "Replay started", session_id=self.session.session_id)

    def pause(self) -> None:
        """Pause replay execution."""
        if self.session.status != ReplayStatus.RUNNING:
            raise ReplayError("Replay can only be paused while running")
        self.clock.pause()
        self.session.status = ReplayStatus.PAUSED
        self.health.report(
            HealthStatus.WARNING,
            {"message": "replay paused"},
        )
        self._dispatch_event(ReplayPausedEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
        log_replay_event(self.logger, "Replay paused", session_id=self.session.session_id)

    def resume(self) -> None:
        """Resume replay execution."""
        if self.session.status != ReplayStatus.PAUSED:
            raise ReplayError("Replay can only resume from paused state")
        self.clock.resume()
        self.session.status = ReplayStatus.RUNNING
        self.health.report(
            HealthStatus.OK,
            {"message": "replay resumed"},
        )
        self._dispatch_event(ReplayResumedEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
        log_replay_event(self.logger, "Replay resumed", session_id=self.session.session_id)

    def stop(self) -> None:
        """Stop replay execution."""
        if self.session.status not in {ReplayStatus.RUNNING, ReplayStatus.PAUSED}:
            raise ReplayError("Replay can only stop while running or paused")
        self.clock.stop()
        self.session.cancel()
        self.health.report(
            HealthStatus.CRITICAL,
            {"message": "replay stopped"},
        )
        self._dispatch_event(ReplayStoppedEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
        log_replay_event(self.logger, "Replay stopped", session_id=self.session.session_id)

    def reset(self) -> None:
        """Reset replay engine to initial state."""
        self.clock.reset()
        self.session.status = ReplayStatus.CREATED
        self.health.report(
            HealthStatus.OK,
            {"message": "replay reset"},
        )
        self.logger.info("Replay reset", extra={"session_id": self.session.session_id})

    def step(self) -> None:
        """Advance replay by a single candle."""
        if self.session.status not in {ReplayStatus.RUNNING, ReplayStatus.PAUSED}:
            raise ReplayError("Replay must be running or paused to step")
        with Timer("replay_step") as _:
            self.clock.step()
            self.session.processed_candles += 1
            if self.clock.current_index >= len(self.buffer):
                self.session.finish()
                self.health.report(
                    HealthStatus.OK,
                    {"message": "replay finished"},
                )
                self._dispatch_event(ReplayFinishedEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
                log_replay_event(self.logger, "Replay finished", session_id=self.session.session_id)
                return
            self._dispatch_event(ReplayStepEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
            log_replay_event(self.logger, "Replay step", session_id=self.session.session_id, index=self.clock.current_index)

    def seek(self, index: int) -> None:
        """Seek replay to a specific candle index."""
        if index < 0 or index >= len(self.buffer):
            raise ReplayError("Seek index out of range")
        with Timer("replay_seek") as _:
            self.clock.seek(index)
        self._dispatch_event(ReplaySeekEvent(self.session.session_id, self.clock.current_time, self.clock.current_index, datetime.utcnow()))
        log_replay_event(self.logger, "Replay seek", session_id=self.session.session_id, index=self.clock.current_index)

    def current_candle(self) -> Candle:
        """Return the current candle from the buffer."""
        return self.buffer.current()

    def current_index(self) -> int:
        """Return the current replay index."""
        return self.clock.current_index

    def remaining(self) -> int:
        """Return the number of remaining candles."""
        return self.buffer.remaining_candles

    def progress(self) -> float:
        """Return replay progress as a fraction."""
        if len(self.buffer) == 0:
            return 0.0
        return self.clock.current_index / len(self.buffer)

    def finished(self) -> bool:
        """Return True when replay has finished."""
        return self.session.status == ReplayStatus.FINISHED

    def _dispatch_event(self, event: ReplayEvent) -> None:
        """Dispatch an event to registered callbacks."""
        with Timer("callback_dispatch") as _:
            self.callbacks.dispatch(event)
