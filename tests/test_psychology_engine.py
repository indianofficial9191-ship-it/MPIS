from datetime import datetime, timedelta

from mpis.data.candle import Candle
from mpis.psychology.engine import PsychologyEngine
from mpis.psychology.models import GapDirection
from mpis.psychology.session import SessionType


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float, symbol: str) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol=symbol, timeframe="1m")


def test_engine_analyze_returns_all_sections() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 15, 0), 100.0, 102.0, 99.0, 101.0, "NIFTY"),
        _candle(datetime(2026, 8, 4, 9, 15), 101.5, 103.0, 100.5, 102.0, "NIFTY"),
        _candle(datetime(2026, 8, 4, 9, 20), 102.0, 104.0, 101.5, 103.0, "NIFTY"),
    ]

    result = PsychologyEngine().analyze(candles)

    assert result.previous_day is not None
    assert result.opening_range is not None
    assert result.session.current_session != None
    assert len(result.psychological_levels) == 1
    assert result.psychological_levels[0].symbol == "NIFTY"


def test_engine_previous_day_gap_direction() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 15, 30), 200.0, 202.0, 198.0, 200.0, "BANKNIFTY"),
        _candle(datetime(2026, 8, 4, 9, 15), 199.0, 201.0, 198.5, 200.5, "BANKNIFTY"),
    ]

    result = PsychologyEngine().analyze(candles)

    assert result.previous_day is not None
    assert result.previous_day.gap_direction == GapDirection.DOWN
    assert result.previous_day.gap_amount == -1.0


def test_engine_opening_range_with_single_day() -> None:
    candles = [
        _candle(datetime(2026, 8, 4, 9, 15), 300.0, 305.0, 299.0, 302.0, "NIFTY"),
        _candle(datetime(2026, 8, 4, 9, 20), 302.0, 306.0, 301.0, 305.0, "NIFTY"),
    ]

    result = PsychologyEngine().analyze(candles)

    assert result.previous_day is None
    assert result.opening_range is not None
    assert result.opening_range.opening_range_high == 306.0
    assert result.opening_range.opening_range_low == 299.0


def test_engine_uses_latest_candle_for_psychological_levels() -> None:
    candles = [
        _candle(datetime(2026, 8, 4, 9, 15), 50.0, 52.0, 49.0, 51.0, "NIFTY"),
        _candle(datetime(2026, 8, 4, 9, 16), 51.0, 52.5, 50.5, 52.0, "NIFTY"),
    ]

    result = PsychologyEngine().analyze(candles)

    assert result.psychological_levels[0].nearest_level == 100.0
    assert result.psychological_levels[0].above_or_below is not None


def test_engine_returns_closing_session_for_last_candle() -> None:
    candles = [
        _candle(datetime(2026, 8, 4, 15, 5), 100.0, 101.0, 99.5, 100.5, "NIFTY"),
    ]

    result = PsychologyEngine().analyze(candles)

    assert result.session.current_session == SessionType.CLOSING_SESSION
    assert result.session.remaining_session_time >= timedelta(0)
