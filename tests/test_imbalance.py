from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import ImbalanceDetector, ImbalanceDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_imbalance_detector_detects_large_displacement() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.5, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 99.8, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.4, 101.2, 100.2, 101.0),
    ]
    detector = ImbalanceDetector(min_body_ratio=0.6, min_range_ratio=0.4)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == ImbalanceDirection.BULLISH
    assert results[0].momentum_score >= 0.5


def test_imbalance_detector_detects_bearish_displacement() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.1, 99.8, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 99.0, 99.5, 98.7, 98.8),
    ]
    detector = ImbalanceDetector(min_body_ratio=0.6, min_range_ratio=0.4)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == ImbalanceDirection.BEARISH


def test_imbalance_detector_ignores_small_move() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.1, 99.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.1, 99.9, 100.0),
    ]
    detector = ImbalanceDetector(min_body_ratio=0.6, min_range_ratio=0.4)

    results = detector.detect(candles)

    assert results == []
