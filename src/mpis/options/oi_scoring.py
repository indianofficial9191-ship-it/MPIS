"""Open interest scoring and signal generation for MPIS."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mpis.options.models import ConfidenceLevel, Direction, OISignal, PositionType
from mpis.options.participant_oi import ParticipantOIHelper
from mpis.options.position_classifier import PositionClassifier
from mpis.utils.logger import get_logger


class OIScorer:
    """Score open interest participant activity into a market signal."""

    def __init__(self) -> None:
        self.logger = get_logger("mpis.options.oi_scoring")

    def compute_participant_scores(self, participants: Sequence[ParticipantOIHelper]) -> dict[str, float]:
        """Compute scores for each participant based on conviction and net open interest."""
        scores: dict[str, float] = {}
        for helper in participants:
            classifier = PositionClassifier.classify_participant(helper)
            score = classifier.conviction * (abs(helper.record.net_oi) + abs(helper.change_balance()))
            if helper.is_trapped_long() or helper.is_trapped_short():
                score *= 1.1
            scores[helper.record.participant_name] = score
            self.logger.debug(
                "Participant score computed",
                extra={
                    "participant": helper.record.participant_name,
                    "position_type": classifier.position_type,
                    "score": score,
                },
            )
        return scores

    def aggregate_signal(self, participants: Sequence[ParticipantOIHelper]) -> OISignal:
        """Aggregate participant opinions into an open interest signal."""
        helpers = list(participants)
        if not helpers:
            return OISignal(
                direction=Direction.NEUTRAL,
                confidence=ConfidenceLevel.LOW,
                score=0.0,
                reason="no participants",
                participant_scores={},
            )

        bullish = 0.0
        bearish = 0.0
        reasons: list[str] = []
        participant_scores = self.compute_participant_scores(helpers)

        for helper in helpers:
            change = helper.change_balance()
            net = helper.record.net_oi
            if helper.is_increasing_long():
                bullish += helper.record.long_change
                reasons.append(f"{helper.record.participant_name} long buildup")
            elif helper.is_increasing_short():
                bearish += helper.record.short_change
                reasons.append(f"{helper.record.participant_name} short buildup")
            elif helper.is_unwinding_long():
                bearish += abs(helper.record.long_change)
                reasons.append(f"{helper.record.participant_name} long unwinding")
            elif helper.is_covering_short():
                bullish += abs(helper.record.short_change)
                reasons.append(f"{helper.record.participant_name} short covering")
            else:
                reasons.append(f"{helper.record.participant_name} sideways")

        score = bullish - bearish
        direction = Direction.NEUTRAL
        if score > 0.0 and abs(score) > 0.2 * max(abs(bullish), abs(bearish), 1.0):
            direction = Direction.BULLISH
        elif score < 0.0 and abs(score) > 0.2 * max(abs(bullish), abs(bearish), 1.0):
            direction = Direction.BEARISH

        confidence_value = min(max(abs(score) / 1000.0, 0.0), 100.0)
        confidence = self._classify_confidence(confidence_value)
        reason = self._assemble_reason(direction, reasons)

        self.logger.info(
            "Open interest signal aggregated",
            extra={"direction": direction.value, "score": score, "confidence": confidence.value},
        )

        return OISignal(
            direction=direction,
            confidence=confidence,
            score=score,
            reason=reason,
            participant_scores=participant_scores,
        )

    def _classify_confidence(self, value: float) -> ConfidenceLevel:
        if value >= 75.0:
            return ConfidenceLevel.VERY_HIGH
        if value >= 50.0:
            return ConfidenceLevel.HIGH
        if value >= 25.0:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _assemble_reason(self, direction: Direction, reasons: list[str]) -> str:
        if direction == Direction.BULLISH:
            return "; ".join(reasons) + ": bullish open interest"
        if direction == Direction.BEARISH:
            return "; ".join(reasons) + ": bearish open interest"
        return "; ".join(reasons) + ": neutral open interest"
