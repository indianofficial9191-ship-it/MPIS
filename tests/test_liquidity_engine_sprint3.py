from datetime import datetime

from mpis.data.candle import Candle
from mpis.liquidity import (
    EqualHighDetector,
    EqualLowDetector,
    LiquidityPoolDetector,
    StopHuntDetector,
    GrabDetector,
    LiquidityEngine,
    EqualHighResult,
    EqualLowResult,
    LiquidityPoolResult,
    StopHuntResult,
    GrabResult,
    LiquidityEngineResult,
)


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_equal_high_detector_detects_clustered_highs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.2, 99.0, 100.2),
        _candle(datetime(2026, 8, 3, 9, 2), 100.2, 100.3, 99.2, 100.3),
    ]
    detector = EqualHighDetector(tolerance=0.3)

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], EqualHighResult)
    assert results[0].touch_count >= 2
    assert results[0].strength >= 0.5


def test_equal_low_detector_detects_clustered_lows() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.5, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.7, 99.1, 100.1),
        _candle(datetime(2026, 8, 3, 9, 2), 100.1, 101.0, 99.2, 100.2),
    ]
    detector = EqualLowDetector(tolerance=0.3)

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], EqualLowResult)
    assert results[0].touch_count >= 2


def test_liquidity_pool_detector_detects_pools() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.1, 98.9, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.1, 100.2, 99.0, 100.1),
    ]
    detector = LiquidityPoolDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], LiquidityPoolResult)
    assert results[0].pool_size >= 2


def test_stop_hunt_detector_detects_sweep_rejection() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.5, 99.0, 100.2),
        _candle(datetime(2026, 8, 3, 9, 2), 100.2, 101.0, 99.5, 100.3),
    ]
    detector = StopHuntDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], StopHuntResult)
    assert results[0].confidence >= 0.8


def test_grab_detector_detects_strong_rejection() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.5, 99.0, 100.4),
        _candle(datetime(2026, 8, 3, 9, 2), 100.4, 101.5, 99.0, 100.1),
    ]
    detector = GrabDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], GrabResult)
    assert results[0].confidence >= 0.8


def test_liquidity_engine_exposes_all_outputs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.2, 99.0, 100.2),
        _candle(datetime(2026, 8, 3, 9, 2), 100.2, 100.4, 99.2, 100.3),
    ]
    engine = LiquidityEngine()

    result = engine.analyze(candles)

    assert isinstance(result, LiquidityEngineResult)
    assert len(result.equal_highs) >= 0
    assert len(result.equal_lows) >= 0
    assert len(result.pools) >= 0
    assert len(result.stop_hunts) >= 0
    assert len(result.liquidity_grabs) >= 0
