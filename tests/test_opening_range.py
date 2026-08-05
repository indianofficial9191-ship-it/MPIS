from datetime import datetime

import pytest

from mpis.data.candle import Candle
from mpis.psychology.opening_range import OpeningRangeAnalyzer
from mpis.psychology.models import OpeningRangeDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_opening_range_calculates_boundaries() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 3, 9, 16), 100.5, 102.0, 100.0, 101.5),
        _candle(datetime(2026, 8, 3, 9, 17), 101.5, 102.5, 101.0, 102.0),
    ]

    result = OpeningRangeAnalyzer(range_minutes=5).analyze(candles)

    assert result.opening_range_high == 102.5
    assert result.opening_range_low == 99.5
    assert result.range_size == 3.0
    assert result.breakout is False
    assert result.breakout_direction == OpeningRangeDirection.NONE
    assert result.fake_breakout is False
    assert result.retest is False


def test_opening_range_detects_breakout_and_retest() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 3, 9, 16), 100.5, 101.0, 100.0, 100.8),
        _candle(datetime(2026, 8, 3, 9, 20), 100.8, 103.0, 100.5, 102.8),
        _candle(datetime(2026, 8, 3, 9, 22), 102.8, 103.5, 101.0, 101.8),
    ]

    result = OpeningRangeAnalyzer(range_minutes=5).analyze(candles)

    assert result.breakout is True
    assert result.breakout_direction == OpeningRangeDirection.UP
    assert result.retest is True
    assert result.fake_breakout is False


def test_opening_range_detects_fake_breakout() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 3, 9, 16), 100.5, 101.2, 100.0, 100.9),
        _candle(datetime(2026, 8, 3, 9, 20), 100.9, 102.0, 100.5, 101.8),
        _candle(datetime(2026, 8, 3, 9, 21), 101.8, 102.0, 100.8, 101.0),
    ]

    result = OpeningRangeAnalyzer(range_minutes=5).analyze(candles)

    assert result.breakout is True
    assert result.fake_breakout is True
    assert result.retest is True


def test_opening_range_raises_for_invalid_range_minutes() -> None:
    with pytest.raises(ValueError):
        OpeningRangeAnalyzer(range_minutes=10).analyze([
            _candle(datetime(2026, 8, 3, 9, 15), 100.0, 101.0, 99.5, 100.5),
        ])


def test_opening_range_handles_single_candle_window() -> None:
    result = OpeningRangeAnalyzer(range_minutes=5).analyze([
        _candle(datetime(2026, 8, 3, 9, 15), 100.0, 101.0, 99.5, 100.5),
    ])

    assert result.opening_range_high == 101.0
    assert result.opening_range_low == 99.5
    assert result.range_size == 1.5
    assert result.breakout is False
