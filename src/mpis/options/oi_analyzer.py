"""Open interest analysis engine for MPIS."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mpis.options.models import OISignal, ParticipantOIRecord, PositionSignal, PositionType
from mpis.options.oi_scoring import OIScorer
from mpis.options.participant_oi import ParticipantOIHelper
from mpis.utils.logger import get_logger


@dataclass(frozen=True)
class OIAnalysisResult:
    """Result of an open interest analysis run."""

    signal_type: PositionType
    signal_strength: float
    position_signal: PositionSignal
    open_interest_signal: OISignal


class OIAnalyzer:
    """Analysis engine for open interest and derivatives intelligence."""

    def __init__(self) -> None:
        self.logger = get_logger("mpis.options.oi_analyzer")
        self.scorer = OIScorer()

    @staticmethod
    def detect_long_buildup(helpers: Sequence[ParticipantOIHelper]) -> bool:
        """Detect long buildup: open interest rising with dominant long additions."""
        long_change = sum(helper.record.long_change for helper in helpers)
        short_change = sum(helper.record.short_change for helper in helpers)
        total_oi_change = long_change + short_change
        return total_oi_change > 0.0 and long_change > 0.0

    @staticmethod
    def detect_short_buildup(helpers: Sequence[ParticipantOIHelper]) -> bool:
        """Detect short buildup: open interest rising with dominant short additions."""
        long_change = sum(helper.record.long_change for helper in helpers)
        short_change = sum(helper.record.short_change for helper in helpers)
        total_oi_change = long_change + short_change
        return total_oi_change > 0.0 and short_change > 0.0

    @staticmethod
    def detect_long_unwinding(helpers: Sequence[ParticipantOIHelper]) -> bool:
        """Detect long unwinding: open interest falling with long decreases."""
        long_change = sum(helper.record.long_change for helper in helpers)
        short_change = sum(helper.record.short_change for helper in helpers)
        total_oi_change = long_change + short_change
        return total_oi_change < 0.0 and long_change < 0.0

    @staticmethod
    def detect_short_covering(helpers: Sequence[ParticipantOIHelper]) -> bool:
        """Detect short covering: open interest falling with short decreases."""
        long_change = sum(helper.record.long_change for helper in helpers)
        short_change = sum(helper.record.short_change for helper in helpers)
        total_oi_change = long_change + short_change
        return total_oi_change < 0.0 and short_change < 0.0

    def analyze(self, records: Sequence[ParticipantOIRecord]) -> object:
        """Analyze participant open interest records and create a signal."""
        helpers = [ParticipantOIHelper(record) for record in records]
        signal = self.scorer.aggregate_signal(helpers)

        signal_type = PositionType.SIDEWAYS
        bullish_count = sum(1 for helper in helpers if helper.is_increasing_long())
        bearish_count = sum(1 for helper in helpers if helper.is_increasing_short())
        long_unwind_count = sum(1 for helper in helpers if helper.is_unwinding_long())
        short_cover_count = sum(1 for helper in helpers if helper.is_covering_short())

        if bullish_count and bearish_count:
            signal_type = PositionType.SIDEWAYS
        elif bullish_count > bearish_count + 0:
            signal_type = PositionType.LONG_BUILDUP
        elif bearish_count > bullish_count + 0:
            signal_type = PositionType.SHORT_BUILDUP
        elif long_unwind_count > 0 and not (bullish_count or bearish_count):
            signal_type = PositionType.LONG_UNWINDING
        elif short_cover_count > 0 and not (bullish_count or bearish_count):
            signal_type = PositionType.SHORT_COVERING
        elif self.detect_long_buildup(helpers):
            signal_type = PositionType.LONG_BUILDUP
        elif self.detect_short_buildup(helpers):
            signal_type = PositionType.SHORT_BUILDUP
        elif self.detect_long_unwinding(helpers):
            signal_type = PositionType.LONG_UNWINDING
        elif self.detect_short_covering(helpers):
            signal_type = PositionType.SHORT_COVERING

        strength = abs(sum(helper.record.long_change for helper in helpers) - sum(helper.record.short_change for helper in helpers))
        position_signal = PositionSignal(
            position_type=signal_type,
            strength=strength,
            confidence=signal.confidence,
            reason=self._position_reason(signal_type),
        )

        self.logger.info(
            "Open interest analysis complete",
            extra={
                "signal_type": signal_type.value,
                "strength": strength,
                "direction": signal.direction.value,
            },
        )

        return OIAnalysisResult(
            signal_type=signal_type,
            signal_strength=strength,
            position_signal=position_signal,
            open_interest_signal=signal,
        )

    @staticmethod
    def _position_reason(position_type: PositionType) -> str:
        return {
            PositionType.LONG_BUILDUP: "long buildup detected",
            PositionType.SHORT_BUILDUP: "short buildup detected",
            PositionType.LONG_UNWINDING: "long unwinding detected",
            PositionType.SHORT_COVERING: "short covering detected",
            PositionType.SIDEWAYS: "sideways open interest",
            PositionType.UNKNOWN: "unknown position state",
        }[position_type]
