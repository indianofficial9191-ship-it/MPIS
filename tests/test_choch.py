from datetime import datetime

from mpis.data.candle import Candle
from mpis.structure.choch import CHOCHConfig, CHOCHDetector, CHOCHDirection
from mpis.structure.models import StructureSignal, StructureType, TrendState


def test_bearish_choch_detects_break_of_previous_high() -> None:
    config = CHOCHConfig(require_close_break=True, minimum_break_points=0.5)
    detector = CHOCHDetector(config)
    swings = [
        StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=105.0, type=StructureType.CHOCH, direction=CHOCHDirection.BEARISH, strength=0.0),
    ]
    candles = [
        Candle(timestamp=datetime(2026, 7, 31, 12, 1), open=104.0, high=105.0, low=103.0, close=103.5, symbol="TEST", timeframe="1m"),
    ]

    results = detector.detect(TrendState.UPTREND, swings, candles)

    assert len(results) == 0


def test_bullish_choch_detects_break_of_previous_low() -> None:
    config = CHOCHConfig(require_close_break=True, minimum_break_points=0.5)
    detector = CHOCHDetector(config)
    swings = [
        StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=95.0, type=StructureType.CHOCH, direction=CHOCHDirection.BULLISH, strength=0.0),
    ]
    candles = [
        Candle(timestamp=datetime(2026, 7, 31, 12, 1), open=96.0, high=98.0, low=95.5, close=96.5, symbol="TEST", timeframe="1m"),
    ]

    results = detector.detect(TrendState.DOWNTREND, swings, candles)

    assert len(results) == 0
