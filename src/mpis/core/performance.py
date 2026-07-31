"""Performance tracking utilities for MPIS."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Iterable


@dataclass
class PerformanceTracker:
    """Tracks named metrics and durations for performance monitoring."""

    metrics: dict[str, float] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)

    def record(self, metric_name: str, value: float) -> None:
        """Record a value for a named metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0.0
            self.counts[metric_name] = 0
        self.metrics[metric_name] += value
        self.counts[metric_name] += 1

    def increment(self, metric_name: str, amount: int = 1) -> None:
        """Increment a count metric."""
        if metric_name not in self.counts:
            self.counts[metric_name] = 0
            self.metrics[metric_name] = 0.0
        self.counts[metric_name] += amount

    def get_average(self, metric_name: str) -> float:
        """Return the average value for a metric."""
        if metric_name not in self.metrics or self.counts.get(metric_name, 0) == 0:
            raise KeyError(f"No data recorded for metric {metric_name}")
        return self.metrics[metric_name] / self.counts[metric_name]

    def get_total(self, metric_name: str) -> float:
        """Return the total value for a metric."""
        if metric_name not in self.metrics:
            raise KeyError(f"No data recorded for metric {metric_name}")
        return self.metrics[metric_name]

    def reset(self, metric_name: str | None = None) -> None:
        """Reset metrics for a specific name or all metrics."""
        if metric_name is None:
            self.metrics.clear()
            self.counts.clear()
            return
        self.metrics.pop(metric_name, None)
        self.counts.pop(metric_name, None)


def track_performance(metric_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to track elapsed time of a function call."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            tracker = getattr(wrapper, "performance_tracker", None)
            if isinstance(tracker, PerformanceTracker):
                tracker.record(metric_name, elapsed)
            return result

        wrapper.performance_tracker = PerformanceTracker()  # type: ignore[attr-defined]
        return wrapper

    return decorator
