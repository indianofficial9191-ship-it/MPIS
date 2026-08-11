"""Sprint 21 live decision orchestration tests."""

from datetime import datetime, timezone

import pytest

from mpis.live.integration import LiveIntegrationEngine
from mpis.live.execution import LiveExecutionGuard
from mpis.live.readiness import LiveReadinessEngine


def test_live_decision_orchestration_accepts_valid_buy():
    readiness = LiveReadinessEngine()
    execution = LiveExecutionGuard()
    integration = LiveIntegrationEngine()

    readiness_result = readiness.evaluate(
        [
            # Sprint 21 orchestration will adapt these inputs
        ]
    )

    assert readiness_result is not None

    execution_result = execution.evaluate([])

    assert execution_result is not None

    integration_result = integration.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.80,
        ready=True,
        execution_allowed=True,
        timestamp=datetime.now(timezone.utc),
    )

    assert integration_result.action == "BUY"
    assert integration_result.blocked is False


def test_live_decision_orchestration_blocks_low_confidence():
    integration = LiveIntegrationEngine()

    result = integration.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.60,
        ready=True,
        execution_allowed=True,
        timestamp=datetime.now(timezone.utc),
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "Confidence" in result.reason


def test_live_decision_orchestration_blocks_failed_readiness():
    integration = LiveIntegrationEngine()

    result = integration.process(
        symbol="BANKNIFTY",
        action="SELL",
        confidence=0.85,
        ready=False,
        execution_allowed=True,
        timestamp=datetime.now(timezone.utc),
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "readiness" in result.reason.lower()


def test_live_decision_orchestration_blocks_execution_guard():
    integration = LiveIntegrationEngine()

    result = integration.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.85,
        ready=True,
        execution_allowed=False,
        timestamp=datetime.now(timezone.utc),
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "Execution guard" in result.reason


def test_live_decision_orchestration_rejects_stale_signal():
    integration = LiveIntegrationEngine()

    stale = datetime.now(timezone.utc).replace(
        year=datetime.now(timezone.utc).year
    )

    # Deliberately use an old timestamp.
    from datetime import timedelta

    stale = datetime.now(timezone.utc) - timedelta(seconds=120)

    result = integration.process(
        symbol="NIFTY",
        action="BUY",
        confidence=0.90,
        ready=True,
        execution_allowed=True,
        timestamp=stale,
    )

    assert result.action == "HOLD"
    assert result.blocked is True
    assert "Stale" in result.reason


def test_live_decision_orchestration_holds_without_trade_action():
    integration = LiveIntegrationEngine()

    result = integration.process(
        symbol="BANKNIFTY",
        action="HOLD",
        confidence=0.50,
        ready=False,
        execution_allowed=False,
        timestamp=datetime.now(timezone.utc),
    )

    assert result.action == "HOLD"
    assert result.blocked is False
    assert result.reason == "No trade signal"


@pytest.mark.parametrize("symbol", ["NIFTY", "BANKNIFTY"])
def test_live_decision_orchestration_supports_target_indices(symbol):
    integration = LiveIntegrationEngine()

    result = integration.process(
        symbol=symbol,
        action="BUY",
        confidence=0.80,
        ready=True,
        execution_allowed=True,
        timestamp=datetime.now(timezone.utc),
    )

    assert result.symbol == symbol
    assert result.action == "BUY"
    assert result.blocked is False
