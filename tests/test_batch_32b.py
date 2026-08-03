from datetime import datetime

from mpis.data.candle import Candle
from mpis.liquidity import (
    LiquidityPoolConfig,
    LiquidityPoolDetector,
    LiquidityPoolResult,
    LiquidityClusterDetector,
    LiquidityClusterResult,
    SwingLiquidityConfig,
    SwingLiquidityDetector,
    SwingLiquidityResult,
    SessionDetector,
    SessionResult,
    SessionType,
)


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_liquidity_pool_detector_detects_clustered_buy_side_liquidity() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 98.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 98.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.1, 100.1, 98.2, 100.1),
        _candle(datetime(2026, 8, 3, 9, 3), 100.2, 100.2, 98.3, 100.2),
    ]
    detector = LiquidityPoolDetector(LiquidityPoolConfig(minimum_touches=2, price_tolerance=0.3))

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], LiquidityPoolResult)
    assert results[0].direction == "buy_side"
    assert results[0].touch_count >= 2
    assert 0.0 <= results[0].confidence <= 1.0


def test_liquidity_cluster_detector_detects_nearby_highs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.5, 99.5, 100.5),
        _candle(datetime(2026, 8, 3, 9, 2), 100.5, 100.6, 99.8, 100.6),
    ]
    detector = LiquidityClusterDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], LiquidityClusterResult)
    assert results[0].cluster_size >= 2
    assert results[0].confidence >= 0.8


def test_swing_liquidity_detector_detects_above_swing_highs() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.5, 99.5, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.5, 101.0, 100.0, 100.5),
        _candle(datetime(2026, 8, 3, 9, 2), 100.8, 103.0, 100.5, 102.5),
    ]
    detector = SwingLiquidityDetector(SwingLiquidityConfig(lookback=2, minimum_swing_distance=1.5))

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], SwingLiquidityResult)
    assert results[0].direction == "above_swing_high"
    assert results[0].confidence >= 0.8


def test_session_detector_tracks_us_session_data() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 30), 100.0, 100.5, 99.0, 100.2),
        _candle(datetime(2026, 8, 3, 10, 0), 100.2, 101.0, 99.8, 100.8),
        _candle(datetime(2026, 8, 3, 10, 30), 100.8, 102.0, 100.0, 101.5),
    ]
    detector = SessionDetector()

    result = detector.detect(candles, session_type=SessionType.US)

    assert result is not None
    assert result.session == SessionType.US
    assert result.high == 102.0
    assert result.low == 99.0
