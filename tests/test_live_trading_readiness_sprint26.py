import pytest

from mpis.live.trading_readiness import (
    TradingReadinessEngine,
    TradingReadinessInput,
    TradingReadinessReason,
    TradingReadinessStatus,
)


def make_input(**overrides):
    data = {
        "symbol": "NIFTY",
        "market_open": True,
        "market_data_healthy": True,
        "decision_ready": True,
        "risk_allowed": True,
        "execution_ready": True,
    }

    data.update(overrides)
    return TradingReadinessInput(**data)


def test_all_checks_passed():
    engine = TradingReadinessEngine()

    result = engine.evaluate(make_input())

    assert result.status is TradingReadinessStatus.READY
    assert result.ready is True
    assert result.reason is TradingReadinessReason.ALL_CHECKS_PASSED
    assert result.failed_checks == ()


def test_market_closed_blocks_readiness():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(market_open=False)
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False
    assert result.reason is TradingReadinessReason.MARKET_CLOSED
    assert "market_open" in result.failed_checks


def test_unhealthy_market_data_blocks_readiness():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(market_data_healthy=False)
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False
    assert result.reason is TradingReadinessReason.MARKET_DATA_UNHEALTHY
    assert "market_data_healthy" in result.failed_checks


def test_decision_not_ready_blocks_readiness():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(decision_ready=False)
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False
    assert result.reason is TradingReadinessReason.DECISION_NOT_READY
    assert "decision_ready" in result.failed_checks


def test_risk_guard_blocks_readiness():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(risk_allowed=False)
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False
    assert result.reason is TradingReadinessReason.RISK_GUARD_BLOCKED
    assert "risk_allowed" in result.failed_checks


def test_execution_not_ready_blocks_readiness():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(execution_ready=False)
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False
    assert result.reason is TradingReadinessReason.EXECUTION_NOT_READY
    assert "execution_ready" in result.failed_checks


def test_multiple_failed_checks_are_reported():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(
            market_open=False,
            market_data_healthy=False,
            decision_ready=False,
            risk_allowed=False,
            execution_ready=False,
        )
    )

    assert result.status is TradingReadinessStatus.NOT_READY
    assert result.ready is False

    assert result.failed_checks == (
        "market_open",
        "market_data_healthy",
        "decision_ready",
        "risk_allowed",
        "execution_ready",
    )


def test_first_failure_reason_is_market_closed():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(
            market_open=False,
            market_data_healthy=False,
            risk_allowed=False,
        )
    )

    assert result.reason is TradingReadinessReason.MARKET_CLOSED


def test_market_data_failure_has_priority_after_session():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(
            market_data_healthy=False,
            decision_ready=False,
            risk_allowed=False,
        )
    )

    assert result.reason is TradingReadinessReason.MARKET_DATA_UNHEALTHY


def test_decision_failure_has_priority_over_risk_failure():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(
            decision_ready=False,
            risk_allowed=False,
            execution_ready=False,
        )
    )

    assert result.reason is TradingReadinessReason.DECISION_NOT_READY


def test_risk_failure_has_priority_over_execution_failure():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(
            risk_allowed=False,
            execution_ready=False,
        )
    )

    assert result.reason is TradingReadinessReason.RISK_GUARD_BLOCKED


def test_execution_failure_is_final_failure():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(execution_ready=False)
    )

    assert result.reason is TradingReadinessReason.EXECUTION_NOT_READY


def test_symbol_is_normalized():
    engine = TradingReadinessEngine()

    result = engine.evaluate(
        make_input(symbol="banknifty")
    )

    assert result.symbol == "BANKNIFTY"
    assert result.ready is True


def test_engine_does_not_mutate_input():
    engine = TradingReadinessEngine()
    request = make_input()

    result = engine.evaluate(request)

    assert request.symbol == "NIFTY"
    assert request.market_open is True
    assert request.market_data_healthy is True
    assert request.decision_ready is True
    assert request.risk_allowed is True
    assert request.execution_ready is True
    assert result.ready is True