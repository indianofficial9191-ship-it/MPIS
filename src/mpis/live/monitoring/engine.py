"""Sprint 13 live monitoring engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import MonitoringInput, MonitoringResult, MonitoringStatus


@dataclass(frozen=True)
class LiveMonitoringEngine:
    stale_after_seconds: float = 60.0
    latency_warning_ms: float = 500.0
    latency_critical_ms: float = 1500.0
    error_warning_rate: float = 0.05
    error_critical_rate: float = 0.20

    def evaluate(
        self,
        inputs: tuple[MonitoringInput, ...] | list[MonitoringInput],
    ) -> MonitoringResult:
        items = tuple(inputs)

        if not items:
            return MonitoringResult(
                status=MonitoringStatus.CRITICAL,
                health_score=0.0,
                reasons=("NO_MONITORING_INPUTS",),
            )

        stale: list[str] = []
        latency: list[str] = []
        errors: list[str] = []
        reasons: list[str] = []

        score = 1.0

        for item in items:
            if not item.active:
                score -= 0.20
                reasons.append(f"{item.name}: INACTIVE")

            if item.age_seconds > self.stale_after_seconds:
                stale.append(item.name)
                score -= 0.25

            if item.latency_ms >= self.latency_critical_ms:
                latency.append(item.name)
                score -= 0.25
            elif item.latency_ms >= self.latency_warning_ms:
                latency.append(item.name)
                score -= 0.10

            if item.error_rate >= self.error_critical_rate:
                errors.append(item.name)
                score -= 0.25
            elif item.error_rate >= self.error_warning_rate:
                errors.append(item.name)
                score -= 0.10

        health_score = max(0.0, min(1.0, score))

        if stale or any(
            item.latency_ms >= self.latency_critical_ms
            or item.error_rate >= self.error_critical_rate
            for item in items
        ):
            status = MonitoringStatus.CRITICAL
        elif health_score < 0.80 or latency or errors:
            status = MonitoringStatus.WARNING
        else:
            status = MonitoringStatus.HEALTHY

        if stale:
            reasons.append("STALE_DATA")
        if latency:
            reasons.append("LATENCY")
        if errors:
            reasons.append("ERROR_RATE")

        return MonitoringResult(
            status=status,
            health_score=health_score,
            stale_sources=tuple(stale),
            latency_sources=tuple(latency),
            error_sources=tuple(errors),
            reasons=tuple(reasons),
        )
