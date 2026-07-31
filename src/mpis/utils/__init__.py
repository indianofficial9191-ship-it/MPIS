"""Utility helpers for MPIS."""
from pathlib import Path
from typing import Iterable

from .logger import get_logger, log_dashboard_event, log_fusion_event, log_replay_event, log_rule_event
from .log_context import LogContext, clear_log_context, get_log_context, set_log_context


def ensure_dirs(paths: Iterable[Path]) -> None:
    """Ensure that each path in ``paths`` exists as a directory.

    Args:
        paths: Iterable of Path objects to create if missing.
    """
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


__all__ = [
    "ensure_dirs",
    "get_logger",
    "log_dashboard_event",
    "log_fusion_event",
    "log_replay_event",
    "log_rule_event",
    "LogContext",
    "clear_log_context",
    "get_log_context",
    "set_log_context",
]
