"""Position classification for open interest signals in MPIS."""
from __future__ import annotations

from mpis.options.models import PositionType
from mpis.options.oi_models import ParticipantOIState
from mpis.options.participant_oi import ParticipantOIHelper


class PositionClassifier:
    """Classifier that determines dominant participant position type."""

    @staticmethod
    def classify_participant(record: ParticipantOIHelper) -> ParticipantOIState:
        """Classify the participant's open interest position state."""
        if record.is_increasing_long():
            return ParticipantOIState(
                participant_name=record.record.participant_name,
                participant_type=record.record.participant_type,
                net_oi=record.record.net_oi,
                long_change=record.record.long_change,
                short_change=record.record.short_change,
                position_type=PositionType.LONG_BUILDUP.value,
                conviction=record.conviction_score(),
            )

        if record.is_increasing_short():
            return ParticipantOIState(
                participant_name=record.record.participant_name,
                participant_type=record.record.participant_type,
                net_oi=record.record.net_oi,
                long_change=record.record.long_change,
                short_change=record.record.short_change,
                position_type=PositionType.SHORT_BUILDUP.value,
                conviction=record.conviction_score(),
            )

        if record.is_unwinding_long():
            return ParticipantOIState(
                participant_name=record.record.participant_name,
                participant_type=record.record.participant_type,
                net_oi=record.record.net_oi,
                long_change=record.record.long_change,
                short_change=record.record.short_change,
                position_type=PositionType.LONG_UNWINDING.value,
                conviction=record.conviction_score(),
            )

        if record.is_covering_short():
            return ParticipantOIState(
                participant_name=record.record.participant_name,
                participant_type=record.record.participant_type,
                net_oi=record.record.net_oi,
                long_change=record.record.long_change,
                short_change=record.record.short_change,
                position_type=PositionType.SHORT_COVERING.value,
                conviction=record.conviction_score(),
            )

        return ParticipantOIState(
            participant_name=record.record.participant_name,
            participant_type=record.record.participant_type,
            net_oi=record.record.net_oi,
            long_change=record.record.long_change,
            short_change=record.record.short_change,
            position_type=PositionType.SIDEWAYS.value,
            conviction=record.conviction_score(),
        )
