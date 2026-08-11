from mpis.live.health import (
    HealthInput,
    HealthStatus,
    LiveHealthEngine,
)


def test_empty_inputs_are_unhealthy():
    result = LiveHealthEngine().evaluate([])

    assert result.status == HealthStatus.UNHEALTHY
    assert result.health_score == 0.0


def test_healthy_live_pipeline():
    inputs = [
        HealthInput("market_data", True, latency_ms=100, error_rate=0.01),
        HealthInput("order_flow", True, latency_ms=150, error_rate=0.01),
        HealthInput("options", True, latency_ms=200, error_rate=0.02),
        HealthInput("confirmation", True, latency_ms=100, error_rate=0.01),
    ]

    result = LiveHealthEngine().evaluate(inputs)

    assert result.status == HealthStatus.HEALTHY
    assert result.health_score >= 0.70
    assert result.stale_warning is False


def test_high_latency_degrades_health():
    inputs = [
        HealthInput("market_data", True, latency_ms=1500, error_rate=0.01),
        HealthInput("order_flow", True, latency_ms=1200, error_rate=0.01),
    ]

    result = LiveHealthEngine().evaluate(inputs)

    assert result.status == HealthStatus.DEGRADED
    assert result.latency_score < 0.0 or result.latency_score == 0.0


def test_high_error_rate_degrades_health():
    inputs = [
        HealthInput("market_data", True, latency_ms=100, error_rate=0.20),
        HealthInput("order_flow", True, latency_ms=100, error_rate=0.20),
    ]

    result = LiveHealthEngine().evaluate(inputs)

    assert result.status == HealthStatus.DEGRADED
    assert result.error_score < 0.0 or result.error_score == 0.0


def test_unhealthy_component_is_reported():
    inputs = [
        HealthInput("market_data", False, latency_ms=100, error_rate=0.01),
        HealthInput("order_flow", True, latency_ms=100, error_rate=0.01),
    ]

    result = LiveHealthEngine().evaluate(inputs)

    assert "market_data" in result.unhealthy_components


def test_stale_component_triggers_warning():
    inputs = [
        HealthInput("market_data", True, latency_ms=100, error_rate=0.01),
        HealthInput(
            "order_flow",
            True,
            latency_ms=100,
            error_rate=0.01,
            stale=True,
        ),
    ]

    result = LiveHealthEngine().evaluate(inputs)

    assert result.stale_warning is True
    assert result.status == HealthStatus.DEGRADED