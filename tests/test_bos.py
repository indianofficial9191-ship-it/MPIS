from datetime import datetime

from mpis.data.candle import Candle
from mpis.structure.bos import BOSConfig, BOSDetector, BreakOfStructureType
from mpis.structure.models import StructureSignal, StructureType, TrendState


def test_bullish_bos_detects_price_close_break() -> None:
    config = BOSConfig(require_close_break=True, minimum_break_points=0.5)
    detector = BOSDetector(config)
    swings = [
        StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=110.0, type=StructureType.BOS, direction=BreakOfStructureType.BULLISH, strength=0.0),
    ]
    candles = [
        Candle(timestamp=datetime(2026, 7, 31, 12, 1), open=109.0, high=111.0, low=108.0, close=111.0, symbol="TEST", timeframe="1m"),
    ]

    results = detector.detect(swings, candles)

    assert len(results) == 1
    assert results[0].direction == BreakOfStructureType.BULLISH


def test_bearish_bos_detects_price_close_break() -> None:
    config = BOSConfig(require_close_break=True, minimum_break_points=0.5)
    detector = BOSDetector(config)
    swings = [
        StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=120.0, type=StructureType.BOS, direction=BreakOfStructureType.BEARISH, strength=0.0),
    ]
    candles = [
        Candle(timestamp=datetime(2026, 7, 31, 12, 1), open=121.0, high=121.0, low=118.0, close=118.5, symbol="TEST", timeframe="1m"),
    ]

    results = detector.detect(swings, candles)

    assert len(results) == 1
    assert results[0].direction == BreakOfStructureType.BEARISH
