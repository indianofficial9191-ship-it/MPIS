"""Callback management for replay events."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Iterable

from mpis.utils.logger import get_logger

from .events import ReplayEvent


class ReplayCallbackRegistry:
    """Registry for replay callbacks."""

    def __init__(self) -> None:
        self._callbacks: list[Callable[[ReplayEvent], Any]] = []
        self.logger = get_logger("mpis.replay.callbacks")

    def register(self, callback: Callable[[ReplayEvent], Any]) -> None:
        """Register a callback to receive replay events."""
        self._callbacks.append(callback)
        self.logger.debug("Callback registered", extra={"callback": repr(callback)})

    def unregister(self, callback: Callable[[ReplayEvent], Any]) -> None:
        """Unregister a previously registered callback."""
        self._callbacks.remove(callback)
        self.logger.debug("Callback unregistered", extra={"callback": repr(callback)})

    def clear(self) -> None:
        """Clear all registered callbacks."""
        self._callbacks.clear()
        self.logger.debug("Callbacks cleared")

    def dispatch(self, event: ReplayEvent) -> None:
        """Dispatch an event to all registered callbacks."""
        for callback in list(self._callbacks):
            try:
                callback(event)
            except Exception as error:
                self.logger.exception("Callback failed", extra={"callback": repr(callback), "error": str(error)})
