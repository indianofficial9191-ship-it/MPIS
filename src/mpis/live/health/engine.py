"""Sprint 12 live pipeline health engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import HealthInput, HealthResult, HealthStatus


@dataclass(frozen=True)
class LiveHealthEngine:
    """Aggregate health evidence before live signal processing."""

    degraded_threshold: float = 0.70
    unhealthy_threshold: float = 0.45
    maximum_latency_ms: float = 1000.0
    maximum_error_rate: float = 0.10

    def evaluate(
        self,
        inputs: tuple[HealthInput, ...] | list[HealthInput],
    ) -> HealthResult:
        items = tuple(inputs)

        if not items:
            return HealthResult(
                status=HealthStatus.UNHEALTHY,
                health_score=0.0,
                latency_score=0.0,
                error_score=0.0,
                stale_warning=False,
            )

        total_weight = 0.0
        health_total = 0.0
        latency_total = 0.0
        error_total = 0.0

        stale_warning = False
        unhealthy: list[str] = []

        for item in items:
            weight = max(0.0, float(item.weight))

            if weight == 0.0:
                continue

            total_weight += weight

            latency = max(0.0, float(item.latency_ms))
            error_rate = max(0.0, min(1.0, float(item.error_rate)))

            latency_score = max(
                0.0,
                min(1.0, 1.0 - latency / self.maximum_latency_ms),
            )

            error_score = max(
                0.0,
                1.0 - error_rate / self.maximum_error_rate,
            )

            component_health = (
                (1.0 if item.healthy else 0.0) * 0.50
                + latency_score * 0.25
                + error_score * 0.25
            )

            health_total += component_health * weight
            latency_total += latency_score * weight
            error_total += error_score * weight

            if item.stale:
                stale_warning = True

            if (
                not item.healthy
                or latency > self.maximum_latency_ms
                or error_rate > self.maximum_error_rate
                or item.stale
            ):
                unhealthy.append(item.name)

        if total_weight == 0.0:
            return HealthResult(
                status=HealthStatus.UNHEALTHY,
                health_score=0.0,
                latency_score=0.0,
                error_score=0.0,
                stale_warning=stale_warning,
            )

        health_score = max(
            0.0,
            min(1.0, health_total / total_weight),
        )

        latency_score = max(
            0.0,
            min(1.0, latency_total / total_weight),
        )

        error_score = max(
            0.0,
            min(1.0, error_total / total_weight),
        )

        has_latency_problem = any(
            max(0.0, float(item.latency_ms)) > self.maximum_latency_ms
            for item in items
            if max(0.0, float(item.weight)) > 0.0
        )

        has_error_problem = any(
            max(0.0, min(1.0, float(item.error_rate)))
            > self.maximum_error_rate
            for item in items
            if max(0.0, float(item.weight)) > 0.0
        )

        has_unhealthy_component = any(
            not item.healthy
            for item in items
            if max(0.0, float(item.weight)) > 0.0
        )

        if (
            health_score < self.unhealthy_threshold
            or has_unhealthy_component
        ):
            status = HealthStatus.UNHEALTHY
        elif (
            health_score < self.degraded_threshold
            or stale_warning
            or has_latency_problem
            or has_error_problem
        ):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthResult(
            status=status,
            health_score=health_score,
            latency_score=latency_score,
            error_score=error_score,
            stale_warning=stale_warning,
            unhealthy_components=tuple(unhealthy),
        )