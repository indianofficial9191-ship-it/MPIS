import csv
from pathlib import Path

import pandas as pd
import pytest

from mpis.options.models import Direction, ParticipantOIRecord, PositionType
from mpis.options.service import OptionOIService


def test_service_from_dataframe_long_buildup() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "long_oi": 120000.0,
                "short_oi": 30000.0,
                "long_change": 6000.0,
                "short_change": 0.0,
                "volume": 90000.0,
                "net_oi": 90000.0,
            }
        ]
    )

    service = OptionOIService()
    result = service.from_dataframe(dataframe)

    assert result.open_interest_signal.direction == Direction.BULLISH
    assert result.signal_type == PositionType.LONG_BUILDUP
    assert result.signal_strength > 0.0


def test_service_from_csv_short_buildup(tmp_path: Path) -> None:
    csv_path = tmp_path / "test.csv"
    rows = [
        {
            "participant_name": "Beta",
            "participant_type": "DII",
            "long_oi": 25000.0,
            "short_oi": 80000.0,
            "long_change": 0.0,
            "short_change": 6000.0,
            "volume": 70000.0,
            "net_oi": -55000.0,
        }
    ]
    dataframe = pd.DataFrame(rows)
    dataframe.to_csv(csv_path, index=False)

    service = OptionOIService()
    result = service.from_csv(csv_path)

    assert result.open_interest_signal.direction == Direction.BEARISH
    assert result.signal_type == PositionType.SHORT_BUILDUP


def test_service_missing_columns_raises() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "long_oi": 120000.0,
                "short_oi": 30000.0,
                "long_change": 6000.0,
                "volume": 90000.0,
                "net_oi": 90000.0,
            }
        ]
    )
    service = OptionOIService()

    with pytest.raises(ValueError):
        service.from_dataframe(dataframe)


def test_mixed_signals_produce_sideways_signal() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Alpha",
                "participant_type": "FII",
                "long_oi": 120000.0,
                "short_oi": 30000.0,
                "long_change": 6000.0,
                "short_change": 0.0,
                "volume": 90000.0,
                "net_oi": 90000.0,
            },
            {
                "participant_name": "Beta",
                "participant_type": "DII",
                "long_oi": 20000.0,
                "short_oi": 80000.0,
                "long_change": 0.0,
                "short_change": 6000.0,
                "volume": 70000.0,
                "net_oi": -60000.0,
            },
        ]
    )
    service = OptionOIService()
    result = service.from_dataframe(dataframe)

    assert result.signal_type == PositionType.SIDEWAYS
    assert result.open_interest_signal.direction == Direction.NEUTRAL


def test_zero_oi_records_return_neutral_signal() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "participant_name": "Neutral",
                "participant_type": "CLIENT",
                "long_oi": 0.0,
                "short_oi": 0.0,
                "long_change": 0.0,
                "short_change": 0.0,
                "volume": 0.0,
                "net_oi": 0.0,
            }
        ]
    )
    service = OptionOIService()
    result = service.from_dataframe(dataframe)

    assert result.open_interest_signal.direction == Direction.NEUTRAL
    assert result.signal_type == PositionType.SIDEWAYS
