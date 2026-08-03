from datetime import datetime

from mpis.data.candle import Candle
from mpis.structure.detector import StructureDetector, StructureDetectorConfig, StructureOutput
from mpis.structure.models import StructureSignal, StructureType, TrendState


def test_structure_detector_identifies_uptrend_and_confidence() -> None:
    config = StructureDetectorConfig()
    detector = StructureDetector(config)
    swings = [
        StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=100.0, type=StructureType.BOS, direction=TrendState.UPTREND, strength=1.0),
        StructureSignal(index=1, timestamp=datetime(2026, 7, 31, 12, 1), price=105.0, type=StructureType.BOS, direction=TrendState.UPTREND, strength=1.0),
    ]
    candles = [
        Candle(timestamp=datetime(2026, 7, 31, 12, 1), open=104.0, high=106.0, low=103.0, close=106.0, symbol="TEST", timeframe="1m"),
    ]

    result = detector.analyze(swings, candles)

    assert isinstance(result, StructureOutput)
    assert result.trend == TrendState.UPTREND
    assert result.confidence >= 0.0
