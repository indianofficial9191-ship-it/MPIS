"""Institutional confirmation engine for Sprint 7."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ConfirmationInput, ConfirmationResult, ConfirmationSide


@dataclass(frozen=True)
class InstitutionalConfirmationEngine:
    """Fuse directional evidence from independent MPIS engines.

    This engine intentionally does not claim that any individual input
    represents verified institutional activity. It only measures agreement
    between upstream research signals.
    """

    minimum_confidence: float = 0.60
    conflict_penalty: float = 0.35

    def analyze(
        self,
        inputs: tuple[ConfirmationInput, ...] | list[ConfirmationInput],
    ) -> ConfirmationResult:
        """Calculate directional alignment and produce BUY/SELL/HOLD."""

        normalized = tuple(inputs)

        if not normalized:
            return ConfirmationResult(
                side=ConfirmationSide.HOLD,
                confidence=0.0,
                alignment_score=0.0,
                bullish_score=0.0,
                bearish_score=0.0,
                conflict_score=0.0,
            )

        bullish = 0.0
        bearish = 0.0
        total_weight = 0.0
        contributors: list[str] = []
        conflicts: list[str] = []

        for item in normalized:
            side = item.side.upper()
            score = max(0.0, min(1.0, float(item.score)))
            weight = max(0.0, float(item.weight))

            if weight == 0.0 or score == 0.0:
                continue

            contribution = score * weight
            total_weight += weight

            if side == "BUY":
                bullish += contribution
                contributors.append(item.name)
            elif side == "SELL":
                bearish += contribution
                contributors.append(item.name)

        if total_weight == 0.0:
            return ConfirmationResult(
                side=ConfirmationSide.HOLD,
                confidence=0.0,
                alignment_score=0.0,
                bullish_score=0.0,
                bearish_score=0.0,
                conflict_score=0.0,
            )

        bullish_ratio = bullish / total_weight
        bearish_ratio = bearish / total_weight

        dominant = max(bullish_ratio, bearish_ratio)
        weaker = min(bullish_ratio, bearish_ratio)

        conflict_score = min(1.0, weaker)

        # Agreement is strong when the dominant direction is large and
        # contradictory evidence is small.
        alignment_score = max(
            0.0,
            min(1.0, dominant - conflict_score * self.conflict_penalty),
        )

        if bullish_ratio > 0 and bearish_ratio > 0:
            conflicts = [
                item.name
                for item in normalized
                if item.side.upper() in {"BUY", "SELL"}
            ]

        if bullish_ratio > bearish_ratio:
            candidate = ConfirmationSide.BUY
        elif bearish_ratio > bullish_ratio:
            candidate = ConfirmationSide.SELL
        else:
            candidate = ConfirmationSide.HOLD

        confidence = alignment_score

        if confidence < self.minimum_confidence:
            candidate = ConfirmationSide.HOLD

        return ConfirmationResult(
            side=candidate,
            confidence=confidence,
            alignment_score=alignment_score,
            bullish_score=bullish_ratio,
            bearish_score=bearish_ratio,
            conflict_score=conflict_score,
            contributors=tuple(contributors),
            conflicts=tuple(conflicts),
        )