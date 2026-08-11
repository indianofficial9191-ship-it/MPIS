from mpis.live.monitoring import (
    LiveMonitoringEngine,
    MonitoringInput,
    MonitoringStatus,
)


def test_empty_inputs_are_critical():
    result = LiveMonitoringEngine().evaluate([])

    assert result.status == MonitoringStatus.CRITICAL
    assert result.health_score == 0.0


def test_healthy_sources():
    inputs = [
        MonitoringInput("market_data", age_seconds=5, latency_ms=100, error_rate=0.0),
        MonitoringInput("order_flow", age_seconds=10, latency_ms=150, error_rate=0.01),
    ]

    result = LiveMonitoringEngine().evaluate(inputs)

    assert result.status == MonitoringStatus.HEALTHY
    assert result.health_score > 0.80


def test_stale_source_is_critical():
    inputs = [
        MonitoringInput("market_data", age_seconds=120, latency_ms=100),
    ]

    result = LiveMonitoringEngine().evaluate(inputs)

    assert result.status == MonitoringStatus.CRITICAL
    assert "market_data" in result.stale_sources


def test_high_latency_is_critical():
    inputs = [
        MonitoringInput("market_data", age_seconds=5, latency_ms=1600),
    ]

    result = LiveMonitoringEngine().evaluate(inputs)

    assert result.status == MonitoringStatus.CRITICAL
    assert "market_data" in result.latency_sources


def test_warning_latency():
    inputs = [
        MonitoringInput("market_data", age_seconds=5, latency_ms=700),
    ]

    result = LiveMonitoringEngine().evaluate(inputs)

    assert result.status == MonitoringStatus.WARNING


def test_high_error_rate_is_critical():
    inputs = [
        MonitoringInput("market_data", age_seconds=5, latency_ms=100, error_rate=0.25),
    ]

    result = LiveMonitoringEngine().evaluate(inputs)

    assert result.status == MonitoringStatus.CRITICAL
    assert "market_data" in result.error_sources
