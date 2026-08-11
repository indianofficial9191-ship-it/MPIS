"""Sprint 10 pipeline decision engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    PipelineDecisionInput,
    PipelineDecisionResult,
    PipelineDecisionSide,
)


@dataclass(frozen=True)
class PipelineDecisionEngine:
    """Final safety-gated decision across MPIS upstream layers."""

    minimum_confidence: float = 0.70
    minimum_alignment: float = 0.65
    maximum_risk: float = 0.60

    def decide(
        self,
        inputs: tuple[PipelineDecisionInput, ...]
        | list[PipelineDecisionInput],
    ) -> PipelineDecisionResult:
        items = tuple(inputs)

        if not items:
            return self._hold()

        buy = 0.0
        sell = 0.0
        total_weight = 0.0
        risk_weight = 0.0
        trap_warning = False

        contributors: list[str] = []
        risk_flags: list[str] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))
            weight = max(0.0, float(item.weight))

            if weight == 0.0:
                continue

            total_weight += weight
            contribution = confidence * weight
            side = item.side.upper()

            if side == "BUY":
                buy += contribution
                contributors.append(item.name)

            elif side == "SELL":
                sell += contribution
                contributors.append(item.name)

            if item.risk_flag:
                risk_weight += weight
                risk_flags.append(item.name)

            if item.trap_flag:
                trap_warning = True

        if total_weight == 0.0:
            return self._hold()

        buy_ratio = buy / total_weight
        sell_ratio = sell / total_weight

        dominant = max(buy_ratio, sell_ratio)
        opposing = min(buy_ratio, sell_ratio)

        alignment = max(
            0.0,
            min(1.0, dominant - opposing * 0.40),
        )

        risk_score = min(
            1.0,
            risk_weight / total_weight,
        )

        confidence = max(
            0.0,
            min(
                1.0,
                alignment - risk_score * 0.25,
            ),
        )

        if buy_ratio > sell_ratio:
            bias = "BULLISH"
        elif sell_ratio > buy_ratio:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        if (
            buy_ratio > sell_ratio
            and confidence >= self.minimum_confidence
            and alignment >= self.minimum_alignment
            and risk_score <= self.maximum_risk
            and not trap_warning
        ):
            side = PipelineDecisionSide.BUY

        elif (
            sell_ratio > buy_ratio
            and confidence >= self.minimum_confidence
            and alignment >= self.minimum_alignment
            and risk_score <= self.maximum_risk
            and not trap_warning
        ):
            side = PipelineDecisionSide.SELL

        else:
            side = PipelineDecisionSide.HOLD

        if side == PipelineDecisionSide.HOLD:
            quality = "WEAK"
        elif confidence >= 0.85:
            quality = "STRONG"
        else:
            quality = "VALID"

        return PipelineDecisionResult(
            side=side,
            confidence=confidence,
            direction_bias=bias,
            alignment_score=alignment,
            risk_score=risk_score,
            trap_warning=trap_warning,
            quality=quality,
            contributors=tuple(contributors),
            risk_flags=tuple(risk_flags),
        )

    @staticmethod
    def _hold() -> PipelineDecisionResult:
        return PipelineDecisionResult(
            side=PipelineDecisionSide.HOLD,
            confidence=0.0,
            direction_bias="NEUTRAL",
            alignment_score=0.0,
            risk_score=0.0,
            trap_warning=False,
            quality="NONE",
        )