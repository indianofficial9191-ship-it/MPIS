"""Centralized logger factory for MPIS."""
from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from .log_context import LogContextFilter, set_log_context
from .log_formatter import MPISLogFormatter

_LOGGER_REGISTRY: Dict[str, logging.Logger] = {}
_LOGGER_LOCK = Lock()


def _get_log_directory(root: Path, logs_path: str) -> Path:
    path = root / logs_path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _configure_logger(name: str, root: Path, logs_path: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = MPISLogFormatter()
    handler_exists = any(isinstance(handler, (logging.StreamHandler, TimedRotatingFileHandler)) for handler in logger.handlers)
    if not handler_exists:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(LogContextFilter())
        logger.addHandler(console_handler)

        log_dir = _get_log_directory(root, logs_path)
        file_handler = TimedRotatingFileHandler(
            log_dir / "mpis.log",
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(LogContextFilter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, root: Optional[Path] = None, logs_path: str = "logs") -> logging.Logger:
    """Return a logger with console and rotating file handlers."""
    with _LOGGER_LOCK:
        if name not in _LOGGER_REGISTRY:
            root_path = root or Path.cwd()
            _LOGGER_REGISTRY[name] = _configure_logger(name, root_path, logs_path)
        return _LOGGER_REGISTRY[name]


def log_rule_event(logger: logging.Logger, event_name: str, **details: Any) -> None:
    """Log a structured rule event."""
    logger.info("Rule event: %s", event_name, extra={"event": details})


def log_replay_event(logger: logging.Logger, event_name: str, **details: Any) -> None:
    """Log a structured replay event."""
    logger.info("Replay event: %s", event_name, extra={"event": details})


def log_fusion_event(logger: logging.Logger, event_name: str, **details: Any) -> None:
    """Log a structured fusion event."""
    logger.info("Fusion event: %s", event_name, extra={"event": details})


def log_dashboard_event(logger: logging.Logger, event_name: str, **details: Any) -> None:
    """Log a structured dashboard event."""
    logger.info("Dashboard event: %s", event_name, extra={"event": details})
