"""Contextual logging utilities for MPIS."""
from __future__ import annotations

import logging
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Dict, Iterator

_context: ContextVar[Dict[str, str]] = ContextVar("mpis_log_context", default={})


def get_log_context() -> Dict[str, str]:
    """Return the current log context values."""
    return _context.get().copy()


def set_log_context(**values: str) -> None:
    """Set or update log context values for the current execution context."""
    current = _context.get().copy()
    current.update(values)
    _context.set(current)


def clear_log_context() -> None:
    """Clear all current log context values."""
    _context.set({})


@dataclass(frozen=True)
class LogContext:
    """Context manager for scoped log context values."""

    values: Dict[str, str]

    def __enter__(self) -> "LogContext":
        token = _context.set({**_context.get(), **self.values})
        object.__setattr__(self, "_token", token)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        _context.reset(self._token)


class LogContextFilter(logging.Filter):
    """Logging filter that injects log context into records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.log_context = get_log_context()
        return True
