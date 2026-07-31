"""Replay runner for MPIS."""
from __future__ import annotations

from datetime import datetime
from typing import overload

from mpis.core.exceptions import ReplayError
from mpis.core.timer import Timer
from mpis.data.candle import Candle
from mpis.replay.engine import ReplayEngine
from mpis.replay.models import ReplaySpeed
from mpis.replay.state import ReplayState


class ReplayRunner:
    """Runner that drives replay execution deterministically."""

    def __init__(self, engine: ReplayEngine) -> None:
        self.engine = engine
        self.timer = Timer("runner")

    def run(self) -> None:
        """Run the replay until completion."""
        if self.engine.finished():
            raise ReplayError("Cannot run finished replay")

        while not self.engine.finished():
            with Timer("runner_step") as _:
                self.engine.step()

    def run_until(self, index: int | None = None, timestamp: datetime | None = None) -> None:
        """Run the replay until a target index or timestamp is reached."""
        if self.engine.finished():
            raise ReplayError("Cannot run finished replay")
        if index is None and timestamp is None:
            raise ReplayError("Either index or timestamp must be provided")

        while not self.engine.finished():
            current = self.engine.current_candle()
            if index is not None and self.engine.current_index() >= index:
                break
            if timestamp is not None and current.timestamp >= timestamp:
                break
            with Timer("runner_step") as _:
                self.engine.step()

    def run_next(self) -> Candle:
        """Step forward once and return the resulting candle."""
        self.engine.step()
        return self.engine.current_candle()

    def run_previous(self) -> Candle:
        """Step backward by moving the buffer cursor to the previous candle."""
        self.engine.buffer.previous()
        return self.engine.current_candle()
