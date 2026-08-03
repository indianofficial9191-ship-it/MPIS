from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import MitigationBlockDetector, MitigationStatus


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_mitigation_block_detector_tracks_partial_and_full_mitigation() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 101.0, 100.2, 100.9),
        _candle(datetime(2026, 8, 3, 9, 2), 100.6, 100.9, 100.1, 100.4),
    ]
    detector = MitigationBlockDetector()

    results = detector.detect(candles, reference_price=100.9)

    assert len(results) == 1
    assert results[0].status == MitigationStatus.PARTIAL
    assert results[0].strength_score >= 0.5


def test_mitigation_block_detector_tracks_full_mitigation() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 101.0, 100.2, 100.9),
        _candle(datetime(2026, 8, 3, 9, 2), 100.8, 100.9, 100.8, 100.9),
    ]
    detector = MitigationBlockDetector()

    results = detector.detect(candles, reference_price=100.9)

    assert len(results) == 1
    assert results[0].status == MitigationStatus.FULL


def test_mitigation_block_detector_returns_empty_outside_range() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.4, 99.8, 100.1),
        _candle(datetime(2026, 8, 3, 9, 1), 100.2, 101.0, 100.2, 100.9),
        _candle(datetime(2026, 8, 3, 9, 2), 101.2, 101.5, 101.1, 101.3),
    ]
    detector = MitigationBlockDetector()

    results = detector.detect(candles, reference_price=100.9)

    assert results == []
