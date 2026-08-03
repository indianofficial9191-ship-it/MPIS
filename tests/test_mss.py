from datetime import datetime

from mpis.structure.mss import MSSConfig, MSSDetector, MSSAnalysis
from mpis.structure.models import StructureSignal, StructureType, TrendState


def test_mss_returns_none_without_choch_or_bos() -> None:
    detector = MSSDetector(MSSConfig())
    swings = []
    candles = []

    result = detector.detect(TrendState.RANGE, swings, candles)

    assert result is None


def test_mss_detects_shift_when_choch_and_bos_present() -> None:
    detector = MSSDetector(MSSConfig())
    signal = StructureSignal(index=0, timestamp=datetime(2026, 7, 31, 12, 0), price=100.0, type=StructureType.BOS, direction=TrendState.UPTREND, strength=1.0)
    candles = [signal]

    result = detector.detect(TrendState.UPTREND, [signal], candles)

    assert isinstance(result, MSSAnalysis)
    assert result.confidence == 1.0
