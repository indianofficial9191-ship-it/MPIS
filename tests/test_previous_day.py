from datetime import datetime

import pytest

from mpis.data.candle import Candle
from mpis.psychology.previous_day import PreviousDayAnalyzer
from mpis.psychology.models import GapDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_previous_day_analysis_detects_gap_up_and_filled() -> None:
    previous_day = [
        _candle(datetime(2026, 8, 1, 15, 15), 100.0, 105.0, 99.0, 102.0),
        _candle(datetime(2026, 8, 1, 15, 30), 102.0, 106.0, 101.0, 105.0),
    ]
    current_day = [
        _candle(datetime(2026, 8, 2, 9, 15), 107.0, 108.0, 104.0, 107.5),
        _candle(datetime(2026, 8, 2, 9, 16), 107.5, 109.0, 105.0, 108.0),
    ]

    result = PreviousDayAnalyzer().analyze(previous_day, current_day)

    assert result.previous_high == 106.0
    assert result.previous_low == 99.0
    assert result.previous_close == 105.0
    assert result.gap_amount == 2.0
    assert result.gap_percent == pytest.approx(1.9048, abs=0.0001)
    assert result.gap_direction == GapDirection.UP
    assert result.gap_filled is True


def test_previous_day_analysis_detects_gap_down_and_unfilled() -> None:
    previous_day = [
        _candle(datetime(2026, 8, 1, 15, 30), 200.0, 205.0, 198.0, 204.0),
    ]
    current_day = [
        _candle(datetime(2026, 8, 2, 9, 15), 202.0, 203.0, 201.0, 202.5),
    ]

    result = PreviousDayAnalyzer().analyze(previous_day, current_day)

    assert result.gap_direction == GapDirection.DOWN
    assert result.gap_amount == -2.0
    assert result.gap_filled is False


def test_previous_day_analysis_without_current_day_sets_no_gap() -> None:
    previous_day = [
        _candle(datetime(2026, 8, 1, 15, 30), 130.0, 135.0, 128.0, 132.0),
    ]

    result = PreviousDayAnalyzer().analyze(previous_day, [])

    assert result.current_open is None
    assert result.gap_direction == GapDirection.NONE
    assert result.gap_amount == 0.0
    assert result.gap_filled is False


def test_previous_day_analysis_requires_previous_day_data() -> None:
    with pytest.raises(ValueError):
        PreviousDayAnalyzer().analyze([], [])


def test_previous_day_analysis_handles_reordered_candles() -> None:
    previous_day = [
        _candle(datetime(2026, 8, 1, 15, 30), 101.0, 105.0, 100.0, 104.0),
        _candle(datetime(2026, 8, 1, 9, 15), 100.0, 103.0, 99.0, 102.0),
    ]
    current_day = [
        _candle(datetime(2026, 8, 2, 9, 15), 106.0, 107.0, 105.0, 106.5),
    ]

    result = PreviousDayAnalyzer().analyze(previous_day, current_day)

    assert result.previous_high == 105.0
    assert result.previous_low == 99.0
    assert result.previous_close == 104.0
    assert result.gap_amount == 2.0
