import pytest

from mpis.core import PerformanceTracker, track_performance


def test_performance_tracker_records_values() -> None:
    tracker = PerformanceTracker()
    tracker.record("db_query", 0.5)
    tracker.record("db_query", 0.3)
    assert tracker.get_total("db_query") == pytest.approx(0.8)
    assert tracker.get_average("db_query") == pytest.approx(0.4)


def test_performance_tracker_reset_metric() -> None:
    tracker = PerformanceTracker()
    tracker.record("api_call", 0.2)
    tracker.reset("api_call")
    with pytest.raises(KeyError):
        tracker.get_total("api_call")


def test_track_performance_decorator() -> None:
    @track_performance("decorated")
    def compute(x: int, y: int) -> int:
        return x + y

    assert hasattr(compute, "performance_tracker")
    result = compute(1, 2)
    assert result == 3
    tracker = getattr(compute, "performance_tracker")
    assert tracker.get_total("decorated") >= 0.0
    assert tracker.get_average("decorated") >= 0.0
