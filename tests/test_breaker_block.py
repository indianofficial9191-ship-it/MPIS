from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import BreakerBlockDetector, OrderBlockDirection, BreakerBlockDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_breaker_block_detector_detects_invalidated_order_block() -> None:
    order_block = {
        "direction": OrderBlockDirection.BULLISH,
        "high": 101.0,
        "low": 100.2,
        "strength": 0.9,
        "timestamp": datetime(2026, 8, 3, 9, 1),
    }
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 101.0, 100.2, 100.9),
        _candle(datetime(2026, 8, 3, 9, 2), 99.8, 100.0, 99.3, 99.5),
    ]
    detector = BreakerBlockDetector()

    results = detector.detect(candles, order_block=order_block)

    assert len(results) == 1
    assert results[0].direction == BreakerBlockDirection.BEARISH
    assert results[0].origin_block["direction"] == OrderBlockDirection.BULLISH


def test_breaker_block_detector_returns_empty_when_not_invalidated() -> None:
    order_block = {
        "direction": OrderBlockDirection.BULLISH,
        "high": 101.0,
        "low": 100.2,
        "strength": 0.9,
        "timestamp": datetime(2026, 8, 3, 9, 1),
    }
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 101.0, 100.2, 100.9),
        _candle(datetime(2026, 8, 3, 9, 2), 100.3, 100.7, 100.1, 100.4),
    ]
    detector = BreakerBlockDetector()

    results = detector.detect(candles, order_block=order_block)

    assert results == []
