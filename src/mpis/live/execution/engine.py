"""Sprint 15 live execution guard."""

from dataclasses import dataclass

from .models import ExecutionInput, ExecutionResult, ExecutionStatus


@dataclass(frozen=True)
class LiveExecutionGuard:
    minimum_confidence: float = 0.65
    maximum_risk: float = 0.60

    def evaluate(
        self,
        inputs: tuple[ExecutionInput, ...] | list[ExecutionInput],
    ) -> ExecutionResult:
        items = tuple(inputs)

        if not items:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                execution_score=0.0,
                reasons=("no_inputs",),
            )

        scores: list[float] = []
        reasons: list[str] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))
            risk = max(0.0, min(1.0, float(item.risk_score)))

            if not item.ready:
                reasons.append(f"{item.name}:not_ready")

            if confidence < self.minimum_confidence:
                reasons.append(f"{item.name}:low_confidence")

            if risk > self.maximum_risk:
                reasons.append(f"{item.name}:high_risk")

            if item.trap_warning:
                reasons.append(f"{item.name}:trap_warning")

            score = confidence * (1.0 - risk)

            if item.trap_warning:
                score *= 0.50

            scores.append(score)

        execution_score = sum(scores) / len(scores)

        if reasons:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                execution_score=execution_score,
                reasons=tuple(reasons),
            )

        return ExecutionResult(
            status=ExecutionStatus.ALLOWED,
            execution_score=execution_score,
            reasons=(),
        )
