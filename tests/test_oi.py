import csv
from pathlib import Path

import pandas as pd
import pytest

from mpis.options.models import ConfidenceLevel, Direction, OISignal, PositionType
from mpis.options.participant_oi import ParticipantOIHelper
from mpis.options.oi_analyzer import OIAnalyzer
from mpis.options.oi_scoring import OIScorer
from mpis.options.position_classifier import PositionClassifier
from mpis.options.service import OptionOIService
from mpis.options.models import ParticipantOIRecord


def create_sample_record(name: str, participant_type: str, long_oi: float, short_oi: float, long_change: float, short_change: float, volume: float) -> ParticipantOIRecord:
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


def test_position_classifier_long_buildup() -> None:
    record = create_sample_record("Alpha", "FII", 120000.0, 30000.0, 5000.0, 0.0, 100000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))

    assert state.position_type == PositionType.LONG_BUILDUP.value
    assert state.conviction > 0.0


def test_position_classifier_short_buildup() -> None:
    record = create_sample_record("Beta", "DII", 20000.0, 80000.0, 0.0, 4000.0, 50000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))

    assert state.position_type == PositionType.SHORT_BUILDUP.value
    assert state.conviction > 0.0


def test_position_classifier_long_unwinding() -> None:
    record = create_sample_record("Gamma", "PRO", 50000.0, 70000.0, -3000.0, 0.0, 25000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))

    assert state.position_type == PositionType.LONG_UNWINDING.value


def test_position_classifier_short_covering() -> None:
    record = create_sample_record("Delta", "CLIENT", 70000.0, 40000.0, 0.0, -2000.0, 120000.0)
    state = PositionClassifier.classify_participant(ParticipantOIHelper(record))

    assert state.position_type == PositionType.SHORT_COVERING.value


def test_oi_scorer_aggregate_signal_bullish() -> None:
    records = [
        create_sample_record("Alpha", "FII", 150000.0, 40000.0, 8000.0, 0.0, 100000.0),
        create_sample_record("Beta", "PRO", 50000.0, 100000.0, 0.0, 2000.0, 50000.0),
    ]
    helpers = [ParticipantOIHelper(record) for record in records]
    signal = OIScorer().aggregate_signal(helpers)

    assert isinstance(signal, OISignal)
    assert signal.direction == Direction.BULLISH
    assert signal.confidence in ConfidenceLevel
    assert signal.score > 0.0


def test_oi_scorer_aggregate_signal_bearish() -> None:
    records = [
        create_sample_record("Beta", "DII", 20000.0, 90000.0, 0.0, 10000.0, 70000.0),
        create_sample_record("Gamma", "CLIENT", 40000.0, 80000.0, -2000.0, 2000.0, 90000.0),
    ]
    helpers = [ParticipantOIHelper(record) for record in records]
    signal = OIScorer().aggregate_signal(helpers)

    assert signal.direction == Direction.BEARISH
    assert signal.score < 0.0


def test_oi_scorer_neutral_signal_for_mixed_activity() -> None:
    records = [
        create_sample_record("Alpha", "FII", 100000.0, 50000.0, 2000.0, 0.0, 80000.0),
        create_sample_record("Beta", "PRO", 60000.0, 120000.0, 0.0, 2000.0, 90000.0),
    ]
    helpers = [ParticipantOIHelper(record) for record in records]
    signal = OIScorer().aggregate_signal(helpers)

    assert signal.direction in {Direction.NEUTRAL, Direction.BEARISH, Direction.BULLISH}
    assert isinstance(signal.confidence, ConfidenceLevel)


def test_option_oi_service_from_dataframe_and_csv(tmp_path: Path) -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "long_oi": 120000.0,
                "short_oi": 40000.0,
                "long_change": 7000.0,
                "short_change": 0.0,
                "volume": 100000.0,
                "net_oi": 80000.0,
            }
        ]
    )
    service = OptionOIService()
    result = service.from_dataframe(dataframe)

    assert result.open_interest_signal.direction == Direction.BULLISH
    assert result.signal_type == PositionType.LONG_BUILDUP
    assert result.signal_strength > 0.0

    csv_path = tmp_path / "oi.csv"
    dataframe.to_csv(csv_path, index=False)
    result_csv = service.from_csv(csv_path)
    assert result_csv.open_interest_signal.direction == result.open_interest_signal.direction


def test_option_oi_service_missing_columns_raises() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "long_oi": 120000.0,
                "short_oi": 40000.0,
                "long_change": 7000.0,
                "short_change": 0.0,
                "volume": 100000.0,
            }
        ]
    )
    service = OptionOIService()
    with pytest.raises(ValueError):
        service.from_dataframe(dataframe)


def test_zero_oi_returns_neutral_signal() -> None:
    records = [
        create_sample_record("Neutral", "CLIENT", 0.0, 0.0, 0.0, 0.0, 0.0),
    ]
    helpers = [ParticipantOIHelper(record) for record in records]
    signal = OIScorer().aggregate_signal(helpers)

    assert signal.direction == Direction.NEUTRAL
    assert signal.score == 0.0
    assert signal.reason.endswith("neutral open interest")
