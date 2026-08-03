from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import BullishFVGDetector, BearishFVGDetector, FVGStatus


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_bullish_fvg_detects_gap() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.5, 99.5, 100.2),
        _candle(datetime(2026, 8, 3, 9, 1), 101.2, 101.8, 100.8, 101.5),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.3, 99.6, 100.1),
    ]
    detector = BullishFVGDetector(min_gap=0.5, fill_percentage=0.5)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].status == FVGStatus.ACTIVE
    assert results[0].gap_size >= 0.5


def test_bearish_fvg_detects_gap() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.3, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 99.0, 99.6, 98.8, 99.2),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.4, 99.8, 100.2),
    ]
    detector = BearishFVGDetector(min_gap=0.4, fill_percentage=0.5)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].status == FVGStatus.ACTIVE


def test_bullish_fvg_marks_filled_when_price_retests_gap() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.5, 99.5, 100.2),
        _candle(datetime(2026, 8, 3, 9, 1), 101.2, 101.8, 100.8, 101.5),
        _candle(datetime(2026, 8, 3, 9, 2), 101.2, 101.4, 101.0, 101.3),
    ]
    detector = BullishFVGDetector(min_gap=0.5, fill_percentage=0.5)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].status == FVGStatus.FILLED


def test_bearish_fvg_ignores_small_gap() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.2, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 99.8, 100.0, 99.7, 99.9),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.1, 99.9, 100.0),
    ]
    detector = BearishFVGDetector(min_gap=0.7, fill_percentage=0.5)

    results = detector.detect(candles)

    assert results == []
