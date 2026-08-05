from datetime import datetime

from mpis.data.candle import Candle
from mpis.psychology.liquidity_grab import LiquidityGrabDetector
from mpis.psychology.models import LiquidityGrabDirection


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_bullish_liquidity_grab_detects_sweep_and_reject() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 100.0, 101.0, 99.5, 100.5),
        _candle(datetime(2026, 8, 5, 9, 16), 100.5, 101.5, 100.0, 101.0),
        _candle(datetime(2026, 8, 5, 9, 17), 101.0, 103.0, 100.5, 101.1),
    ]

    results = LiquidityGrabDetector().detect(candles)

    assert results[0].found is True
    assert results[0].direction == LiquidityGrabDirection.BULLISH
    assert results[0].close_back_inside is True


def test_bearish_liquidity_grab_detects_sweep_and_reject() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 130.0, 131.0, 129.0, 130.5),
        _candle(datetime(2026, 8, 5, 9, 16), 130.5, 131.0, 129.0, 130.0),
        _candle(datetime(2026, 8, 5, 9, 17), 130.0, 130.5, 127.0, 129.5),
    ]

    results = LiquidityGrabDetector().detect(candles)

    assert results[0].found is True
    assert results[0].direction == LiquidityGrabDirection.BEARISH
    assert results[0].close_back_inside is True


def test_no_liquidity_grab_returns_negative_result() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 90.0, 91.0, 89.5, 90.5),
        _candle(datetime(2026, 8, 5, 9, 16), 90.5, 91.5, 90.0, 91.0),
        _candle(datetime(2026, 8, 5, 9, 17), 91.0, 92.0, 90.5, 91.8),
    ]

    results = LiquidityGrabDetector().detect(candles)

    assert results[0].found is False
    assert results[0].confidence == 0.0


def test_liquidity_grab_confidence_is_within_bounds() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 200.0, 201.0, 199.0, 200.5),
        _candle(datetime(2026, 8, 5, 9, 16), 200.5, 203.0, 200.0, 202.0),
        _candle(datetime(2026, 8, 5, 9, 17), 202.0, 204.0, 201.0, 202.5),
    ]

    result = LiquidityGrabDetector().detect(candles)[0]

    assert 0.0 <= result.confidence <= 1.0


def test_liquidity_grab_considers_rejection_price() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 80.0, 81.0, 79.0, 80.0),
        _candle(datetime(2026, 8, 5, 9, 16), 80.0, 82.0, 79.0, 79.5),
        _candle(datetime(2026, 8, 5, 9, 17), 79.5, 82.5, 79.0, 80.5),
    ]

    result = LiquidityGrabDetector().detect(candles)[0]

    assert result.rejection_price == 80.5
    assert result.sweep_price == 82.5
