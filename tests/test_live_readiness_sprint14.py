from mpis.live.readiness import (
    LiveReadinessEngine,
    ReadinessInput,
    ReadinessStatus,
)


def test_empty_inputs_block():
    result = LiveReadinessEngine().evaluate([])

    assert result.status == ReadinessStatus.BLOCKED
    assert result.readiness_score == 0.0


def test_healthy_inputs_ready():
    inputs = [
        ReadinessInput("market_data", True, 0.90),
        ReadinessInput("order_flow", True, 0.85),
        ReadinessInput("signal", True, 0.90),
    ]

    result = LiveReadinessEngine().evaluate(inputs)

    assert result.status == ReadinessStatus.READY
    assert result.readiness_score >= 0.70


def test_unhealthy_input_blocks():
    inputs = [
        ReadinessInput("market_data", False, 0.90),
        ReadinessInput("signal", True, 0.90),
    ]

    result = LiveReadinessEngine().evaluate(inputs)

    assert result.status == ReadinessStatus.BLOCKED
    assert "market_data" in result.blocked_reasons


def test_risk_input_degrades():
    inputs = [
        ReadinessInput("market_data", True, 0.90),
        ReadinessInput("signal", True, 0.90, risk_flag=True),
    ]

    result = LiveReadinessEngine().evaluate(inputs)

    assert result.status == ReadinessStatus.DEGRADED
    assert "signal" in result.degraded_reasons


def test_low_confidence_degrades():
    inputs = [
        ReadinessInput("market_data", True, 0.50),
        ReadinessInput("signal", True, 0.55),
    ]

    result = LiveReadinessEngine().evaluate(inputs)

    assert result.status == ReadinessStatus.DEGRADED
