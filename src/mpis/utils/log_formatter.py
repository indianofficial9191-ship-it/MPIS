"""Log formatter for MPIS logs."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from .log_context import get_log_context


class MPISLogFormatter(logging.Formatter):
    """Formatter that renders rich structured log records."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        module = record.name
        func = record.funcName
        level = record.levelname
        message = record.getMessage()
        context = get_log_context()
        context_str = " ".join(f"{key}={value}" for key, value in context.items())
        if context_str:
            return f"{timestamp} | {level} | {module} | {func} | {message} | {context_str}"
        return f"{timestamp} | {level} | {module} | {func} | {message}"

    def formatException(self, ei: Any) -> str:
        return super().formatException(ei)
