from datetime import datetime, timedelta

import pytest

from mpis.data.candle import Candle
from mpis.liquidity import (
    EqualHighDetector,
    EqualLowDetector,
    LiquiditySweepConfig,
    LiquiditySweepDetector,
    LiquiditySweepDirection,
)
from mpis.liquidity.stop_hunt import StopHuntDetector


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_liquidity_sweep_detects_buy_side_sweep() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 3), 102.0, 103.0, 101.0, 102.0),
        _candle(datetime(2026, 8, 3, 9, 4), 102.0, 103.5, 101.5, 103.0),
    ]

    detector = LiquiditySweepDetector(LiquiditySweepConfig(lookback=3, minimum_sweep_distance=1.0))

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == LiquiditySweepDirection.BUY_SIDE
    assert results[0].confidence >= 0.8
    assert results[0].swept_price == pytest.approx(100.0)
    assert results[0].confirmation_price == pytest.approx(103.0)


def test_stop_hunt_detector_detects_above_highs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 101.0, 101.0, 100.0, 101.0),
        _candle(datetime(2026, 8, 3, 9, 3), 99.0, 105.0, 98.0, 99.5),
    ]

    detector = StopHuntDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].direction == "above_highs"
    assert results[0].confidence >= 0.8


def test_equal_high_detector_detects_equal_highs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.5, 100.5, 99.5, 100.5),
        _candle(datetime(2026, 8, 3, 9, 2), 99.0, 100.0, 98.5, 99.0),
    ]

    detector = EqualHighDetector(tolerance=0.6)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].price == pytest.approx(100.0)


def test_equal_low_detector_detects_equal_lows() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 102.0, 99.0, 101.0),
        _candle(datetime(2026, 8, 3, 9, 1), 101.0, 103.0, 99.5, 102.0),
        _candle(datetime(2026, 8, 3, 9, 2), 102.0, 104.0, 99.0, 103.0),
    ]

    detector = EqualLowDetector(tolerance=0.6)

    results = detector.detect(candles)

    assert len(results) == 1
    assert results[0].price == pytest.approx(99.0)
