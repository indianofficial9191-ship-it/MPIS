"""Timer utilities for MPIS."""
from __future__ import annotations

import time
from contextlib import AbstractContextManager
from typing import Callable, Iterator


class Timer(AbstractContextManager[float]):
    """A simple context-managed timer for measuring elapsed time."""

    def __init__(self, label: str | None = None) -> None:
        self.label = label
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.elapsed: float | None = None

    def __enter__(self) -> float:
        self.start_time = time.perf_counter()
        self.end_time = None
        self.elapsed = None
        return self.start_time

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: object | None) -> bool:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        return False

    def reset(self) -> None:
        """Reset the timer state for reuse."""
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def get_elapsed(self) -> float:
        """Return the last recorded elapsed time.

        Raises:
            RuntimeError: If the timer has not been stopped.
        """
        if self.elapsed is None:
            raise RuntimeError("Timer has not been stopped yet")
        return self.elapsed

    def __repr__(self) -> str:
        return f"<Timer label={self.label!r} elapsed={self.elapsed!r}>"
