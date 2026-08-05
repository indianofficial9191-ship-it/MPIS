from datetime import datetime

from mpis.data.candle import Candle
from mpis.psychology.stop_hunt import StopHuntConfig, StopHuntDetector, StopHuntSide


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_buy_side_stop_hunt_detects_large_lower_wick() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 100.0, 105.0, 99.0, 104.0),
        _candle(datetime(2026, 8, 5, 9, 16), 104.0, 107.0, 95.0, 105.5),
    ]

    detector = StopHuntDetector()
    results = detector.detect(candles)

    assert results[-1].found is True
    assert results[-1].side == StopHuntSide.BUY
    assert results[-1].confidence > 0.0


def test_sell_side_stop_hunt_detects_large_upper_wick() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 110.0, 115.0, 109.0, 112.0),
        _candle(datetime(2026, 8, 5, 9, 16), 114.0, 120.0, 112.0, 113.0),
    ]

    detector = StopHuntDetector()
    results = detector.detect(candles)

    assert results[-1].found is True
    assert results[-1].side == StopHuntSide.SELL
    assert results[-1].confidence > 0.0


def test_stop_hunt_requires_minimum_wick_and_penetration() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 150.0, 152.0, 149.0, 151.0),
        _candle(datetime(2026, 8, 5, 9, 16), 151.0, 153.0, 150.5, 152.0),
    ]

    detector = StopHuntDetector()
    results = detector.detect(candles)

    assert results[-1].found is False
    assert results[-1].confidence == 0.0


def test_stop_hunt_is_configurable() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 120.0, 125.0, 119.0, 124.0),
        _candle(datetime(2026, 8, 5, 9, 16), 124.0, 126.0, 118.0, 125.5),
    ]

    detector = StopHuntDetector(StopHuntConfig(min_wick_pct=20.0, min_penetration_pct=5.0))
    results = detector.detect(candles)

    assert results[-1].found is True
    assert results[-1].side == StopHuntSide.BUY


def test_stop_hunt_returns_one_result_per_checked_candle() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 90.0, 92.0, 89.0, 91.0),
        _candle(datetime(2026, 8, 5, 9, 16), 91.0, 94.0, 88.0, 92.5),
        _candle(datetime(2026, 8, 5, 9, 17), 92.5, 93.0, 90.0, 91.5),
    ]

    detector = StopHuntDetector()
    results = detector.detect(candles)

    assert len(results) == 2
    assert all(isinstance(result.found, bool) for result in results)
