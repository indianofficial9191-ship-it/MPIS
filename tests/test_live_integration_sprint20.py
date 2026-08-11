"""Sprint 20 live integration tests."""

from datetime import datetime, timezone

import pytest

from mpis.live.integration import (
    LiveIntegrationEngine,
    LiveIntegrationResult,
)


def make_engine() -> LiveIntegrationEngine:
    return LiveIntegrationEngine()


def test_engine_can_be_created() -> None:
    engine = make_engine()

    assert engine is not None


def test_empty_pipeline_returns_no_signal() -> None:
    engine = make_engine()

    result = engine.process()

    assert isinstance(result, LiveIntegrationResult)
    assert result.action == "HOLD"


def test_buy_signal_reaches_final_output() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.85,
    )

    assert result.action == "BUY"
    assert result.symbol == "NIFTY"
    assert result.confidence >= 0.85


def test_sell_signal_reaches_final_output() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="SELL",
        confidence=0.85,
    )

    assert result.action == "SELL"
    assert result.symbol == "NIFTY"


def test_low_confidence_becomes_hold() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.40,
    )

    assert result.action == "HOLD"
    assert result.blocked is True


def test_readiness_failure_blocks_signal() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.90,
        ready=False,
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "readiness" in result.reason.lower()


def test_execution_guard_failure_blocks_signal() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.90,
        ready=True,
        execution_allowed=False,
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "guard" in result.reason.lower()


def test_stale_signal_is_rejected() -> None:
    engine = make_engine()

    old_timestamp = datetime(
        2020,
        1,
        1,
        tzinfo=timezone.utc,
    )

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.90,
        timestamp=old_timestamp,
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "stale" in result.reason.lower()


def test_invalid_confidence_is_rejected() -> None:
    engine = make_engine()

    with pytest.raises(ValueError, match="confidence"):
        engine.process(
            symbol="NIFTY",
            action="BUY",
            confidence=1.50,
        )


def test_invalid_symbol_is_rejected() -> None:
    engine = make_engine()

    with pytest.raises(ValueError, match="symbol"):
        engine.process(
            symbol="",
            action="BUY",
            confidence=0.90,
        )


def test_hold_is_preserved() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="HOLD",
        confidence=0.50,
    )

    assert result.action == "HOLD"
    assert result.blocked is False


def test_result_is_deterministic() -> None:
    engine = make_engine()

    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.85,
        timestamp=timestamp,
    )

    second = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.85,
        timestamp=timestamp,
    )

    assert first.action == second.action
    assert first.symbol == second.symbol
    assert first.confidence == second.confidence
    assert first.blocked == second.blocked


def test_banknifty_is_supported() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="BANKNIFTY",
        action="SELL",
        confidence=0.90,
    )

    assert result.symbol == "BANKNIFTY"
    assert result.action == "SELL"


def test_missing_execution_permission_blocks_trade() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="BANKNIFTY",
        action="SELL",
        confidence=0.90,
        ready=True,
        execution_allowed=False,
    )

    assert result.action == "HOLD"
    assert result.blocked is True


def test_safe_signal_contains_reason() -> None:
    engine = make_engine()

    result = engine.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.90,
        ready=True,
        execution_allowed=True,
    )

    assert result.action == "BUY"
    assert result.blocked is False
    assert result.reason
