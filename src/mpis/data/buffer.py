"""Replay buffer for MPIS market data."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

from mpis.core.exceptions import DataError
from mpis.core.timer import Timer
from mpis.data.candle import Candle
from mpis.data.models import DataHealthStatus
from mpis.data.validator import DataHealth, DataValidator
from mpis.utils.logger import get_logger


@dataclass
class ReplayBuffer:
    """In-memory buffer for replay candle data."""

    candles: list[Candle] = field(default_factory=list)
    current_index: int = 0
    validator: DataValidator = field(default_factory=DataValidator)
    health: DataHealth = field(default_factory=DataHealth)
    logger: object = field(default_factory=lambda: get_logger("mpis.data.buffer"))

    def __post_init__(self) -> None:
        with Timer("buffer_creation") as _:
            self.candles = list(self.candles)
        self._validate_buffer()
        self.health.report(DataHealthStatus.OK, "buffer created")
        self.logger.info("Buffer created", extra={"size": len(self.candles)})

    def _validate_buffer(self) -> None:
        self.validator.validate_candles(self.candles)

    def append(self, candle: Candle) -> None:
        """Append a candle to the buffer and validate ordering."""
        self.candles.append(candle)
        self._validate_buffer()
        self.logger.info("Candle appended to buffer", extra={"current_size": len(self.candles)})

    def extend(self, candles: Iterable[Candle]) -> None:
        """Extend the buffer with multiple candles."""
        with Timer("buffer_extension") as _:
            self.candles.extend(candles)
        self._validate_buffer()
        self.logger.info("Buffer extended", extra={"current_size": len(self.candles)})

    def clear(self) -> None:
        """Clear the buffer and reset the current index."""
        self.candles.clear()
        self.current_index = 0
        self.health.report(DataHealthStatus.UNKNOWN, "buffer cleared")
        self.logger.info("Buffer cleared")

    def current(self) -> Candle:
        """Return the current candle."""
        if not self.candles:
            raise DataError("Buffer is empty")
        return self.candles[self.current_index]

    def next(self) -> Candle:
        """Advance to the next candle and return it."""
        if self.current_index + 1 >= len(self.candles):
            raise DataError("No next candle available")
        self.current_index += 1
        candle = self.current()
        self.logger.info("Buffer advanced to next candle", extra={"current_index": self.current_index})
        return candle

    def previous(self) -> Candle:
        """Return the previous candle and move the cursor back."""
        if self.current_index == 0:
            raise DataError("No previous candle available")
        self.current_index -= 1
        candle = self.current()
        self.logger.info("Buffer moved to previous candle", extra={"current_index": self.current_index})
        return candle

    def peek(self, offset: int = 1) -> Candle:
        """Return a candle at an offset from the current position."""
        target_index = self.current_index + offset
        if target_index < 0 or target_index >= len(self.candles):
            raise DataError("Peek index out of range")
        return self.candles[target_index]

    def seek(self, index: int) -> None:
        """Seek to a specific candle index."""
        if index < 0 or index >= len(self.candles):
            raise DataError(f"Seek index {index} is out of range")
        self.current_index = index
        self.logger.info("Buffer seeked", extra={"current_index": self.current_index})

    def slice(self, start: int, end: int) -> list[Candle]:
        """Return a slice of candles from the buffer."""
        if start < 0 or end < 0 or start > end or end > len(self.candles):
            raise DataError("Invalid slice boundaries")
        return list(self.candles[start:end])

    def __len__(self) -> int:
        return len(self.candles)

    def __iter__(self) -> Iterator[Candle]:
        return iter(self.candles)

    def __getitem__(self, index: int) -> Candle:
        return self.candles[index]

    @property
    def remaining_candles(self) -> int:
        """Return the number of candles remaining after the current one."""
        return len(self.candles) - self.current_index - 1
