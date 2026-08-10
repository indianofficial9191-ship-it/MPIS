"""Sprint 8 final MPIS decision gate."""

from __future__ import annotations

from dataclasses import dataclass

from .models import DecisionEvidence, DecisionResult, DecisionSide


@dataclass(frozen=True)
class DecisionEngine:
    minimum_confidence: float = 0.65
    maximum_conflict: float = 0.40
    maximum_risk: float = 0.60

    def decide(
        self,
        evidence: tuple[DecisionEvidence, ...] | list[DecisionEvidence],
    ) -> DecisionResult:
        items = tuple(evidence)

        if not items:
            return DecisionResult(
                side=DecisionSide.HOLD,
                confidence=0.0,
                bullish_score=0.0,
                bearish_score=0.0,
                conflict_score=0.0,
                risk_score=0.0,
                signal_quality="NONE",
            )

        bullish = 0.0
        bearish = 0.0
        total_weight = 0.0
        risk_weight = 0.0
        contributors: list[str] = []
        risk_flags: list[str] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))
            weight = max(0.0, float(item.weight))

            if weight == 0.0:
                continue

            contribution = confidence * weight
            total_weight += weight

            side = item.side.upper()

            if side == "BUY":
                bullish += contribution
                contributors.append(item.name)
            elif side == "SELL":
                bearish += contribution
                contributors.append(item.name)

            if item.risk_flag:
                risk_weight += weight
                risk_flags.append(item.name)

        if total_weight == 0.0:
            return DecisionResult(
                side=DecisionSide.HOLD,
                confidence=0.0,
                bullish_score=0.0,
                bearish_score=0.0,
                conflict_score=0.0,
                risk_score=0.0,
                signal_quality="NONE",
            )

        bullish_score = bullish / total_weight
        bearish_score = bearish / total_weight

        dominant = max(bullish_score, bearish_score)
        weaker = min(bullish_score, bearish_score)

        conflict_score = min(1.0, weaker)
        risk_score = min(1.0, risk_weight / total_weight)

        confidence = max(
            0.0,
            min(1.0, dominant - (conflict_score * 0.40) - (risk_score * 0.25)),
        )

        if (
            bullish_score > bearish_score
            and confidence >= self.minimum_confidence
            and conflict_score <= self.maximum_conflict
            and risk_score <= self.maximum_risk
        ):
            side = DecisionSide.BUY
        elif (
            bearish_score > bullish_score
            and confidence >= self.minimum_confidence
            and conflict_score <= self.maximum_conflict
            and risk_score <= self.maximum_risk
        ):
            side = DecisionSide.SELL
        else:
            side = DecisionSide.HOLD

        if side == DecisionSide.HOLD:
            quality = "WEAK"
        elif confidence >= 0.80:
            quality = "STRONG"
        else:
            quality = "VALID"

        return DecisionResult(
            side=side,
            confidence=confidence,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            conflict_score=conflict_score,
            risk_score=risk_score,
            signal_quality=quality,
            contributors=tuple(contributors),
            risk_flags=tuple(risk_flags),
        )