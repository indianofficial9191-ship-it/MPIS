from datetime import datetime

from mpis.data.candle import Candle
from mpis.liquidity import (
    FakeBreakoutDetector,
    FakeBreakoutResult,
    InducementDetector,
    InducementResult,
    LiquidityPoolDetector,
    LiquidityPoolResult,
    RoundNumberPsychologyDetector,
    RoundNumberPsychologyResult,
    SessionHighDetector,
    SessionHighResult,
    SessionLowDetector,
    SessionLowResult,
)


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_fake_breakout_detector_detects_breakout() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 101.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 101.5, 99.5, 101.0),
        _candle(datetime(2026, 8, 3, 9, 2), 101.0, 103.0, 100.0, 102.0),
    ]
    detector = FakeBreakoutDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], FakeBreakoutResult)
    assert results[0].confidence >= 0.8
    assert results[0].direction == "up"


def test_inducement_detector_detects_retest() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 101.0, 99.0, 100.5),
        _candle(datetime(2026, 8, 3, 9, 1), 100.5, 102.0, 100.0, 101.5),
        _candle(datetime(2026, 8, 3, 9, 2), 101.0, 102.5, 100.5, 102.0),
    ]
    detector = InducementDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], InducementResult)
    assert results[0].confidence >= 0.8


def test_liquidity_pool_detector_detects_pool() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.5, 101.0, 99.5, 100.5),
    ]
    detector = LiquidityPoolDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], LiquidityPoolResult)
    assert results[0].confidence >= 0.8


def test_session_high_detector_detects_session_high() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 101.0, 101.0, 100.0, 101.0),
        _candle(datetime(2026, 8, 3, 9, 2), 102.0, 102.0, 101.0, 102.0),
    ]
    detector = SessionHighDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], SessionHighResult)
    assert results[0].price == 102.0


def test_session_low_detector_detects_session_low() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 101.0, 101.0, 100.0, 101.0),
        _candle(datetime(2026, 8, 3, 9, 2), 102.0, 102.0, 99.0, 102.0),
    ]
    detector = SessionLowDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], SessionLowResult)
    assert results[0].price == 99.0


def test_round_number_psychology_detector_detects_round_number() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.0, 99.0, 100.0),
        _candle(datetime(2026, 8, 3, 9, 1), 101.0, 101.0, 100.0, 101.0),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.0, 99.0, 100.0),
    ]
    detector = RoundNumberPsychologyDetector()

    results = detector.detect(candles)

    assert len(results) == 1
    assert isinstance(results[0], RoundNumberPsychologyResult)
    assert results[0].confidence >= 0.8
