"""Institutional analysis orchestration for MPIS."""
from __future__ import annotations

from typing import Sequence

from mpis.institutional.classifier import InstitutionalClassifier
from mpis.institutional.models import InstitutionalSignal, MarketState, ParticipantRecord
from mpis.institutional.psychology import PsychologyEngine
from mpis.institutional.scoring import InstitutionalScorer
from mpis.utils.logger import get_logger


class InstitutionalAnalyzer:
    """Analyze institutional participant data to generate market signals."""

    def __init__(self) -> None:
        self.logger = get_logger("mpis.institutional.analyzer")

    def analyze(self, participants: Sequence[ParticipantRecord]) -> InstitutionalSignal:
        """Produce an institutional signal from participant records."""
        self.logger.info("Starting institutional analysis", extra={"participants": len(participants)})

        bullish_score = sum(max(0.0, p.equity_net + p.future_net + p.option_net) for p in participants)
        bearish_score = sum(max(0.0, -(p.equity_net + p.future_net + p.option_net)) for p in participants)
        neutral_score = sum(abs(p.oi_change) for p in participants) / 1_000_000.0

        psychology = PsychologyEngine()
        psychology_state = MarketState.NEUTRAL
        reason = "institutional psychology analysis"

        if psychology.detect_long_buildup(participants):
            psychology_state = MarketState.STRONG_BULLISH
            reason = "long buildup detected"
        elif psychology.detect_short_buildup(participants):
            psychology_state = MarketState.STRONG_BEARISH
            reason = "short buildup detected"
        elif psychology.detect_accumulation(participants):
            psychology_state = MarketState.BULLISH
            reason = "accumulation detected"
        elif psychology.detect_distribution(participants):
            psychology_state = MarketState.BEARISH
            reason = "distribution detected"

        participant_scores = InstitutionalScorer.compute_scores(participants)
        confidence_score = InstitutionalScorer.normalize_score(participant_scores)
        confidence = InstitutionalClassifier.classify_confidence(confidence_score)
        classifier_state = InstitutionalClassifier.classify_market_state(bullish_score, bearish_score)

        state = psychology_state if psychology_state != MarketState.NEUTRAL else classifier_state

        signal = InstitutionalSignal(
            direction=state,
            confidence=confidence,
            score=confidence_score,
            reason=reason,
            participant_scores=participant_scores,
        )

        self.logger.info(
            "Institutional analysis complete",
            extra={
                "direction": signal.direction.value,
                "confidence": signal.confidence.value,
                "score": signal.score,
                "reason": signal.reason,
                "neutral_score": neutral_score,
            },
        )

        return signal
