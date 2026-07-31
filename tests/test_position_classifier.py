from mpis.options.models import PositionType
from mpis.options.participant_oi import ParticipantOIHelper
from mpis.options.position_classifier import PositionClassifier
from mpis.options.models import ParticipantOIRecord


def create_record(name: str, participant_type: str, long_oi: float, short_oi: float, long_change: float, short_change: float, volume: float) -> ParticipantOIRecord:
    return ParticipantOIRecord(
        participant_name=name,
        participant_type=participant_type,
        long_oi=long_oi,
        short_oi=short_oi,
        long_change=long_change,
        short_change=short_change,
        volume=volume,
        net_oi=long_oi - short_oi,
    )


def test_classify_participant_long_buildup() -> None:
    record = create_record("FII_A", "FII", 150000.0, 50000.0, 8000.0, 0.0, 90000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))
    assert state.position_type == PositionType.LONG_BUILDUP.value


def test_classify_participant_short_buildup() -> None:
    record = create_record("DII_A", "DII", 40000.0, 110000.0, 0.0, 7000.0, 85000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))
    assert state.position_type == PositionType.SHORT_BUILDUP.value


def test_classify_participant_long_unwinding() -> None:
    record = create_record("PRO_A", "PRO", 50000.0, 60000.0, -3000.0, 0.0, 30000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))
    assert state.position_type == PositionType.LONG_UNWINDING.value


def test_classify_participant_short_covering() -> None:
    record = create_record("CLIENT_A", "CLIENT", 90000.0, 50000.0, 0.0, -4000.0, 120000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))
    assert state.position_type == PositionType.SHORT_COVERING.value


def test_classify_participant_sideways() -> None:
    record = create_record("Neutral_A", "FII", 100000.0, 100000.0, 0.0, 0.0, 50000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))
    assert state.position_type == PositionType.SIDEWAYS.value
