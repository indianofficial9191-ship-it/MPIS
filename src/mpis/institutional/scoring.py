"""Institutional scoring utilities for MPIS."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Sequence

from mpis.institutional.models import ParticipantRecord
from mpis.institutional.participant import ParticipantHelper


DEFAULT_WEIGHTS: dict[str, float] = {
    "FII": 40.0,
    "DII": 25.0,
    "PRO": 25.0,
    "CLIENT": 10.0,
}


@dataclass(frozen=True)
class ParticipantScore:
    """Score details for a participant group."""

    name: str
    value: float
    weight: float


class InstitutionalScorer:
    """Score institutional participants to generate a combined signal."""

    @staticmethod
    def compute_scores(participants: Sequence[ParticipantRecord]) -> dict[str, float]:
        """Compute weighted participant scores for a set of records."""
        totals: dict[str, float] = {key: 0.0 for key in DEFAULT_WEIGHTS}
        counts: dict[str, int] = {key: 0 for key in DEFAULT_WEIGHTS}

        for record in participants:
            helper = ParticipantHelper(record)
            net = helper.net_position()
            totals[record.participant_type.value] += net
            counts[record.participant_type.value] += 1

        scores: dict[str, float] = {}
        for key, total in totals.items():
            weight = DEFAULT_WEIGHTS[key]
            if counts[key] > 0:
                scores[key] = max(min(total * weight / 1_000_000.0, 100.0), -100.0)
            else:
                scores[key] = 0.0

        return scores

    @staticmethod
    def normalize_score(participant_scores: Mapping[str, float]) -> float:
        """Normalize participant scores into a 0-100 overall value."""
        positive = sum(score for score in participant_scores.values() if score > 0)
        negative = sum(abs(score) for score in participant_scores.values() if score < 0)
        raw = positive - negative
        normalized = max(min((raw / 200.0) * 100.0 + 50.0, 100.0), 0.0)
        return normalized
