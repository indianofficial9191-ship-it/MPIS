"""Sprint 14 live decision readiness engine."""

from dataclasses import dataclass

from .models import ReadinessInput, ReadinessResult, ReadinessStatus


@dataclass(frozen=True)
class LiveReadinessEngine:
    minimum_readiness: float = 0.70
    minimum_confidence: float = 0.65

    def evaluate(
        self,
        inputs: tuple[ReadinessInput, ...] | list[ReadinessInput],
    ) -> ReadinessResult:
        items = tuple(inputs)

        if not items:
            return ReadinessResult(
                status=ReadinessStatus.BLOCKED,
                readiness_score=0.0,
                confidence=0.0,
                blocked_reasons=("no_inputs",),
            )

        blocked: list[str] = []
        degraded: list[str] = []
        scores: list[float] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))

            if not item.healthy:
                blocked.append(item.name)
                continue

            if item.risk_flag:
                degraded.append(item.name)
                scores.append(confidence * 0.50)
            else:
                scores.append(confidence)

        if blocked:
            return ReadinessResult(
                status=ReadinessStatus.BLOCKED,
                readiness_score=0.0,
                confidence=0.0,
                blocked_reasons=tuple(blocked),
                degraded_reasons=tuple(degraded),
            )

        if not scores:
            return ReadinessResult(
                status=ReadinessStatus.BLOCKED,
                readiness_score=0.0,
                confidence=0.0,
                blocked_reasons=("no_healthy_inputs",),
                degraded_reasons=tuple(degraded),
            )

        readiness = sum(scores) / len(scores)
        confidence = readiness

        if (
            readiness >= self.minimum_readiness
            and confidence >= self.minimum_confidence
            and not degraded
        ):
            status = ReadinessStatus.READY
        else:
            status = ReadinessStatus.DEGRADED

        return ReadinessResult(
            status=status,
            readiness_score=readiness,
            confidence=confidence,
            blocked_reasons=tuple(blocked),
            degraded_reasons=tuple(degraded),
        )
