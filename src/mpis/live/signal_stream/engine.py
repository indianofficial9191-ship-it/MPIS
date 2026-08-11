"""Sprint 18 live signal stream engine."""

from __future__ import annotations

from collections import deque
from threading import RLock

from .models import SignalEvent, SignalStreamSnapshot


class SignalStreamEngine:
    """In-memory live signal event stream.

    The engine accepts validated signal events, assigns an increasing
    sequence number, retains a bounded history, and exposes the latest
    signal for each symbol.
    """

    def __init__(self, max_history: int = 1000) -> None:
        if max_history <= 0:
            raise ValueError("max_history must be positive")

        self._history: deque[SignalEvent] = deque(maxlen=max_history)
        self._latest: dict[str, SignalEvent] = {}
        self._sequence = 0
        self._lock = RLock()

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def event_count(self) -> int:
        return len(self._history)

    def publish(self, event: SignalEvent) -> int:
        """Publish one signal event and return its stream sequence."""
        self._validate(event)

        with self._lock:
            self._sequence += 1
            self._history.append(event)
            self._latest[event.symbol] = event
            return self._sequence

    def latest(self, symbol: str) -> SignalEvent | None:
        """Return the latest signal for a symbol."""
        if not symbol:
            raise ValueError("symbol must not be empty")

        with self._lock:
            return self._latest.get(symbol)

    def history(self, symbol: str | None = None) -> tuple[SignalEvent, ...]:
        """Return retained events, optionally filtered by symbol."""
        with self._lock:
            events = tuple(self._history)

        if symbol is None:
            return events

        if not symbol:
            raise ValueError("symbol must not be empty")

        return tuple(event for event in events if event.symbol == symbol)

    def snapshot(self, symbol: str) -> SignalStreamSnapshot:
        """Return the current stream state for one symbol."""
        if not symbol:
            raise ValueError("symbol must not be empty")

        with self._lock:
            return SignalStreamSnapshot(
                symbol=symbol,
                latest=self._latest.get(symbol),
                event_count=sum(
                    1 for event in self._history if event.symbol == symbol
                ),
                sequence=self._sequence,
            )

    def clear(self) -> None:
        """Clear retained events and latest-signal state."""
        with self._lock:
            self._history.clear()
            self._latest.clear()
            self._sequence = 0

    @staticmethod
    def _validate(event: SignalEvent) -> None:
        if not event.signal_id:
            raise ValueError("signal_id must not be empty")

        if not event.symbol:
            raise ValueError("symbol must not be empty")

        if not 0.0 <= event.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")