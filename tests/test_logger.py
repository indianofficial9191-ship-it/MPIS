"""Tests for the MPIS logging subsystem."""
from __future__ import annotations

import logging
from pathlib import Path
import tempfile

from mpis.utils.logger import (
    get_logger,
    log_dashboard_event,
    log_fusion_event,
    log_replay_event,
    log_rule_event,
)
from mpis.utils.log_context import LogContext, clear_log_context, get_log_context


def test_logger_singleton_returns_same_instance(tmp_path: Path) -> None:
    logger_a = get_logger("mpis_test", root=tmp_path, logs_path="logs")
    logger_b = get_logger("mpis_test", root=tmp_path, logs_path="logs")
    assert logger_a is logger_b


def test_log_directory_created(tmp_path: Path) -> None:
    _ = get_logger("mpis_dir_test", root=tmp_path, logs_path="logs")
    assert (tmp_path / "logs").exists()
    assert (tmp_path / "logs" / "mpis.log").exists()


def test_console_and_rotating_handlers_exist(tmp_path: Path) -> None:
    logger = get_logger("mpis_handler_test", root=tmp_path, logs_path="logs")
    handler_types = {type(handler) for handler in logger.handlers}
    assert logging.StreamHandler in handler_types
    assert any(type(handler).__name__ == "TimedRotatingFileHandler" for handler in logger.handlers)


def test_structured_event_helpers(tmp_path: Path) -> None:
    logger = get_logger("mpis_event_test", root=tmp_path, logs_path="logs")
    log_rule_event(logger, "TestRule", rule="X")
    log_replay_event(logger, "TestReplay", step=1)
    log_fusion_event(logger, "TestFusion", status="ok")
    log_dashboard_event(logger, "TestDashboard", widget="foo")
    assert (tmp_path / "logs" / "mpis.log").exists()


def test_log_context_manager() -> None:
    clear_log_context()
    with LogContext({"Market": "NIFTY", "Mode": "Replay"}):
        context = get_log_context()
        assert context["Market"] == "NIFTY"
        assert context["Mode"] == "Replay"
    assert get_log_context() == {}
