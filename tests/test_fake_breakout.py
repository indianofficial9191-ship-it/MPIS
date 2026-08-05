from datetime import datetime

from mpis.data.candle import Candle
from mpis.psychology.fake_breakout import FakeBreakoutDetector
from mpis.psychology.models import FakeBreakoutConfig, FakeBreakoutType


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_false_opening_range_break_detects_reversal() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 5, 9, 16), 100.5, 101.5, 100.0, 101.2),
        _candle(datetime(2026, 8, 5, 9, 17), 101.2, 101.8, 100.5, 100.8),
        _candle(datetime(2026, 8, 5, 9, 18), 100.8, 101.0, 100.0, 100.2),
    ]

    detector = FakeBreakoutDetector(FakeBreakoutConfig(confirmation_candles=2))
    results = detector.detect(candles, opening_range_high=101.0)

    assert any(result.breakout_type == FakeBreakoutType.FALSE_OPENING_RANGE for result in results)
    assert any(result.direction == "up" for result in results)


def test_false_pdh_break_detects_reversal_below_previous_high() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 150.0, 151.0, 149.0, 150.5),
        _candle(datetime(2026, 8, 5, 9, 16), 150.5, 152.0, 150.0, 151.5),
        _candle(datetime(2026, 8, 5, 9, 17), 151.5, 152.0, 150.5, 150.8),
    ]

    detector = FakeBreakoutDetector(FakeBreakoutConfig(confirmation_candles=1))
    results = detector.detect(candles, previous_day_high=151.0)

    assert any(result.breakout_type == FakeBreakoutType.FALSE_PDH_BREAK for result in results)
    assert any(result.direction == "up" for result in results)


def test_false_bos_detects_range_break_failure() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 120.0, 121.0, 119.0, 120.5),
        _candle(datetime(2026, 8, 5, 9, 16), 120.5, 123.0, 120.0, 122.0),
        _candle(datetime(2026, 8, 5, 9, 17), 122.0, 123.0, 120.5, 121.0),
    ]

    detector = FakeBreakoutDetector(FakeBreakoutConfig(confirmation_candles=1))
    results = detector.detect(candles)

    assert any(result.breakout_type == FakeBreakoutType.FALSE_BOS for result in results)


def test_false_choch_detects_structure_failure() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 12), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 5, 9, 13), 100.5, 102.0, 100.0, 101.5),
        _candle(datetime(2026, 8, 5, 9, 14), 101.5, 103.0, 101.0, 102.5),
        _candle(datetime(2026, 8, 5, 9, 15), 102.5, 104.0, 102.0, 103.5),
        _candle(datetime(2026, 8, 5, 9, 16), 103.5, 104.0, 101.5, 102.0),
    ]

    detector = FakeBreakoutDetector(FakeBreakoutConfig(confirmation_candles=1))
    results = detector.detect(candles)

    assert any(result.breakout_type == FakeBreakoutType.FALSE_CHOCH for result in results)


def test_fake_breakout_returns_empty_when_breakout_holds() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 5, 9, 16), 100.5, 104.0, 100.0, 103.5),
        _candle(datetime(2026, 8, 5, 9, 17), 103.5, 104.5, 103.0, 104.0),
    ]

    detector = FakeBreakoutDetector(FakeBreakoutConfig(confirmation_candles=1))
    results = detector.detect(candles)

    assert results == []
