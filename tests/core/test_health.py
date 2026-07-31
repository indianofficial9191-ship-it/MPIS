import pytest

from mpis.core import HealthMonitor, HealthStatus


def test_health_monitor_defaults_to_ok() -> None:
    monitor = HealthMonitor()
    assert monitor.is_healthy()
    assert monitor.status == HealthStatus.OK
    assert monitor.summary()["details"] == {}


def test_health_monitor_report_warning() -> None:
    monitor = HealthMonitor()
    monitor.report(HealthStatus.WARNING, {"latency": "high"})
    assert monitor.status == HealthStatus.WARNING
    assert monitor.summary()["details"]["latency"] == "high"
    assert not monitor.is_healthy()


def test_health_monitor_add_and_clear_details() -> None:
    monitor = HealthMonitor()
    monitor.add_detail("load", "medium")
    assert monitor.summary()["details"]["load"] == "medium"
    monitor.clear_details()
    assert monitor.summary()["details"] == {}
