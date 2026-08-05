from datetime import datetime

from mpis.data.candle import Candle
from mpis.psychology.models import TrapType
from mpis.psychology.trap_detector import TrapDetector


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_bull_trap_detects_false_upside_breakout_with_bearish_rejection() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 100.0, 101.0, 99.0, 100.5),
        _candle(datetime(2026, 8, 5, 9, 16), 100.5, 105.0, 100.0, 104.5),
        _candle(datetime(2026, 8, 5, 9, 17), 104.5, 105.0, 101.0, 102.0),
        _candle(datetime(2026, 8, 5, 9, 18), 102.0, 106.0, 100.0, 101.0),
    ]

    result = TrapDetector().detect(candles)

    assert result.trap_type == TrapType.BULL_TRAP
    assert result.liquidity_detected is True
    assert result.structure_detected is True
    assert result.rejection_detected is True
    assert result.confidence > 0.0


def test_bear_trap_detects_false_downside_breakout_with_bullish_rejection() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 200.0, 202.0, 199.0, 200.5),
        _candle(datetime(2026, 8, 5, 9, 16), 200.5, 201.0, 195.0, 196.0),
        _candle(datetime(2026, 8, 5, 9, 17), 196.0, 199.5, 195.5, 199.5),
        _candle(datetime(2026, 8, 5, 9, 18), 198.5, 203.0, 193.0, 199.5),
    ]

    result = TrapDetector().detect(candles)

    assert result.trap_type == TrapType.BEAR_TRAP
    assert result.liquidity_detected is True
    assert result.structure_detected is True
    assert result.rejection_detected is True


def test_trap_detector_returns_none_when_structure_missing() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 110.0, 112.0, 109.0, 111.0),
        _candle(datetime(2026, 8, 5, 9, 16), 111.0, 113.0, 110.0, 112.5),
        _candle(datetime(2026, 8, 5, 9, 17), 112.5, 114.0, 112.0, 113.5),
        _candle(datetime(2026, 8, 5, 9, 18), 113.5, 115.0, 113.0, 114.0),
    ]

    result = TrapDetector().detect(candles)

    assert result.trap_type == TrapType.NONE
    assert result.structure_detected is False


def test_trap_detector_returns_none_when_liquidity_missing() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 160.0, 162.0, 159.0, 161.0),
        _candle(datetime(2026, 8, 5, 9, 16), 161.0, 163.0, 160.0, 162.0),
        _candle(datetime(2026, 8, 5, 9, 17), 162.0, 164.0, 161.0, 163.0),
        _candle(datetime(2026, 8, 5, 9, 18), 163.0, 165.0, 162.0, 164.0),
    ]

    result = TrapDetector().detect(candles)

    assert result.trap_type == TrapType.NONE
    assert result.liquidity_detected is False


def test_trap_detector_requires_enough_candles() -> None:
    candles = [
        _candle(datetime(2026, 8, 5, 9, 15), 220.0, 221.0, 219.0, 220.5),
        _candle(datetime(2026, 8, 5, 9, 16), 220.5, 222.0, 220.0, 221.0),
    ]

    result = TrapDetector().detect(candles)

    assert result.trap_type == TrapType.NONE
    assert result.confidence == 0.0
