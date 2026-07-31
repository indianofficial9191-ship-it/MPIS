import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from mpis.core.exceptions import DataError, ValidationError
from mpis.data import CSVLoader, Candle, DataHealthStatus, DataValidator, ReplayBuffer


def test_candle_properties() -> None:
    candle = Candle(
        timestamp=datetime(2026, 7, 31, 12, 0),
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        symbol="TEST",
        timeframe="1m",
        volume=1000.0,
        oi=10.0,
    )

    assert candle.bullish is True
    assert candle.bearish is False
    assert candle.body == 5.0
    assert candle.upper_wick == 5.0
    assert candle.lower_wick == 10.0
    assert candle.range == 20.0
    assert candle.typical_price == pytest.approx(101.6666666667)
    assert candle.median_price == 100.0
    assert candle.weighted_price == 102.5


def test_invalid_candle_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Candle(
            timestamp=datetime(2026, 7, 31, 12, 0),
            open=-1.0,
            high=110.0,
            low=90.0,
            close=105.0,
            symbol="TEST",
            timeframe="1m",
        )


def test_csv_loader_loads_and_sorts(tmp_path: Path) -> None:
    csv_path = tmp_path / "test.csv"
    rows = [
        ("2026-07-31", "12:00:02", 103.0, 108.0, 101.0, 105.0, 1200.0, 5.0),
        ("2026-07-31", "12:00:01", 100.0, 110.0, 95.0, 105.0, 1300.0, 6.0),
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "time", "open", "high", "low", "close", "volume", "oi"])
        writer.writerows(rows)

    loader = CSVLoader()
    buffer = loader.load(csv_path, "TEST", "1m")

    assert len(buffer) == 2
    assert buffer.current().timestamp == datetime(2026, 7, 31, 12, 0, 1)
    assert buffer[1].timestamp == datetime(2026, 7, 31, 12, 0, 2)
    assert buffer.remaining_candles == 1
    assert loader.health.status == DataHealthStatus.OK


def test_csv_loader_rejects_duplicate_timestamps(tmp_path: Path) -> None:
    csv_path = tmp_path / "duplicate.csv"
    rows = [
        ("2026-07-31", "12:00:00", 100.0, 110.0, 95.0, 105.0, 1200.0, 5.0),
        ("2026-07-31", "12:00:00", 101.0, 111.0, 96.0, 104.0, 1300.0, 6.0),
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "time", "open", "high", "low", "close", "volume", "oi"])
        writer.writerows(rows)

    loader = CSVLoader()
    with pytest.raises(DataError):
        loader.load(csv_path, "TEST", "1m")


def test_replay_buffer_navigation(tmp_path: Path) -> None:
    candles = [
        Candle(datetime(2026, 7, 31, 12, 0, 0), 100.0, 105.0, 95.0, 102.0, "TEST", "1m"),
        Candle(datetime(2026, 7, 31, 12, 1, 0), 102.0, 108.0, 101.0, 107.0, "TEST", "1m"),
        Candle(datetime(2026, 7, 31, 12, 2, 0), 107.0, 109.0, 106.0, 108.0, "TEST", "1m"),
    ]
    buffer = ReplayBuffer(candles)

    assert len(buffer) == 3
    assert buffer.current().timestamp == candles[0].timestamp
    assert buffer.next().timestamp == candles[1].timestamp
    assert buffer.peek(1).timestamp == candles[2].timestamp
    assert buffer.previous().timestamp == candles[0].timestamp
    buffer.seek(2)
    assert buffer.current().timestamp == candles[2].timestamp
    assert buffer.slice(0, 2) == candles[:2]


def test_buffer_invalid_operations_raise_error() -> None:
    buffer = ReplayBuffer([])
    with pytest.raises(DataError):
        buffer.current()
    with pytest.raises(DataError):
        buffer.next()
    with pytest.raises(DataError):
        buffer.previous()
    with pytest.raises(DataError):
        buffer.peek(0)
    with pytest.raises(DataError):
        buffer.seek(0)
    with pytest.raises(DataError):
        buffer.slice(2, 1)


def test_data_validator_rejects_invalid_dataframe() -> None:
    validator = DataValidator()
    dataframe = pd.DataFrame(
        {
            "timestamp": [datetime(2026, 7, 31, 12, 0, 0), datetime(2026, 7, 31, 11, 0, 0)],
            "open": [100.0, 101.0],
            "high": [110.0, 111.0],
            "low": [90.0, 91.0],
            "close": [105.0, 106.0],
        }
    )
    with pytest.raises(DataError):
        validator.validate_dataframe(dataframe)
