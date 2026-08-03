from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import OrderBlockDetector, OrderBlockDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_order_block_detector_identifies_bullish_block() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 100.7, 100.0, 100.5),
        _candle(datetime(2026, 8, 3, 9, 2), 100.8, 101.2, 100.5, 101.0),
        _candle(datetime(2026, 8, 3, 9, 3), 100.9, 101.3, 100.6, 101.1),
        _candle(datetime(2026, 8, 3, 9, 4), 100.5, 100.8, 100.1, 100.6),
    ]
    detector = OrderBlockDetector(min_body_ratio=0.5)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == OrderBlockDirection.BULLISH
    assert results[0].freshness == 1
    assert results[0].validity == "valid"


def test_order_block_detector_identifies_bearish_block() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 100.7, 100.0, 100.5),
        _candle(datetime(2026, 8, 3, 9, 2), 99.4, 99.8, 99.0, 99.2),
        _candle(datetime(2026, 8, 3, 9, 3), 99.2, 99.6, 99.0, 99.3),
        _candle(datetime(2026, 8, 3, 9, 4), 99.5, 99.9, 99.3, 99.7),
    ]
    detector = OrderBlockDetector(min_body_ratio=0.5)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == OrderBlockDirection.BEARISH


def test_order_block_detector_returns_empty_for_weak_body_ratio() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 3), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 4), 100.0, 100.1, 99.9, 100.0),
    ]
    detector = OrderBlockDetector(min_body_ratio=0.5)

    results = detector.detect(candles)

    assert results == []
