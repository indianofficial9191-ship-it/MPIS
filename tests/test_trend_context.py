from dataclasses import dataclass
from datetime import datetime

from mpis.psychology.models import TrendContext, TrendStrength
from mpis.psychology.trend import TrendContextEngine


@dataclass(frozen=True)
class Signal:
    direction: str
    timestamp: datetime


@dataclass(frozen=True)
class MSSAnalysis:
    trend: str
    confidence: float
    timestamp: datetime


@dataclass(frozen=True)
class SwingPoint:
    type: str
    price: float
    timestamp: datetime


def test_no_signals_returns_sideways_context() -> None:
    engine = TrendContextEngine()
    result = engine.analyze()

    assert isinstance(result, TrendContext)
    assert result.trend == TrendStrength.SIDEWAYS
    assert result.confidence == 0.0
    assert result.bos_confirmed is False
    assert result.choch_confirmed is False
    assert result.mss_confirmed is False
    assert result.swing_highs == []
    assert result.swing_lows == []
    assert result.timestamp == datetime(1970, 1, 1)


def test_bos_and_mss_agreement_produces_very_bullish_trend() -> None:
    engine = TrendContextEngine()
    bos = [Signal(direction="up", timestamp=datetime(2026, 8, 5, 10, 0))]
    mss = MSSAnalysis(trend="uptrend", confidence=0.85, timestamp=datetime(2026, 8, 5, 10, 1))
    swings = [
        SwingPoint(type="high", price=108.0, timestamp=datetime(2026, 8, 5, 9, 59)),
        SwingPoint(type="low", price=102.0, timestamp=datetime(2026, 8, 5, 9, 58)),
    ]

    result = engine.analyze(trend_state="uptrend", bos_signals=bos, choch_signals=(), mss_analysis=mss, swings=swings)

    assert result.trend == TrendStrength.VERY_BULLISH
    assert result.confidence >= 0.6
    assert result.bos_confirmed is True
    assert result.mss_confirmed is True
    assert result.swing_highs == [108.0]
    assert result.swing_lows == [102.0]
    assert result.timestamp == datetime(2026, 8, 5, 10, 1)


def test_choch_reduces_trend_strength() -> None:
    engine = TrendContextEngine()
    bos = [Signal(direction="up", timestamp=datetime(2026, 8, 5, 10, 0))]
    choch = [Signal(direction="down", timestamp=datetime(2026, 8, 5, 10, 2))]
    mss = MSSAnalysis(trend="uptrend", confidence=0.7, timestamp=datetime(2026, 8, 5, 10, 1))

    result = engine.analyze(trend_state="uptrend", bos_signals=bos, choch_signals=choch, mss_analysis=mss, swings=())

    assert result.trend == TrendStrength.BULLISH
    assert result.confidence < 0.7
    assert result.choch_confirmed is True


def test_downtrend_with_bos_and_mss_returns_very_bearish() -> None:
    engine = TrendContextEngine()
    bos = [Signal(direction="down", timestamp=datetime(2026, 8, 5, 11, 0))]
    mss = MSSAnalysis(trend="downtrend", confidence=0.9, timestamp=datetime(2026, 8, 5, 11, 1))

    result = engine.analyze(trend_state="downtrend", bos_signals=bos, choch_signals=(), mss_analysis=mss, swings=())

    assert result.trend == TrendStrength.VERY_BEARISH
    assert result.bos_confirmed is True
    assert result.mss_confirmed is True


def test_swing_highs_and_lows_from_swings_are_extracted() -> None:
    engine = TrendContextEngine()
    swings = [
        SwingPoint(type="high", price=130.0, timestamp=datetime(2026, 8, 5, 12, 0)),
        SwingPoint(type="low", price=125.0, timestamp=datetime(2026, 8, 5, 12, 5)),
        SwingPoint(type="high", price=131.0, timestamp=datetime(2026, 8, 5, 12, 10)),
    ]

    result = engine.analyze(trend_state="range", bos_signals=(), choch_signals=(), mss_analysis=None, swings=swings)

    assert result.swing_highs == [130.0, 131.0]
    assert result.swing_lows == [125.0]
    assert result.trend == TrendStrength.SIDEWAYS
    assert result.timestamp == datetime(2026, 8, 5, 12, 10)


def test_mss_direction_without_bos_infers_weak_strength() -> None:
    engine = TrendContextEngine()
    mss = MSSAnalysis(trend="uptrend", confidence=0.6, timestamp=datetime(2026, 8, 5, 13, 0))

    result = engine.analyze(trend_state="range", bos_signals=(), choch_signals=(), mss_analysis=mss, swings=())

    assert result.trend == TrendStrength.WEAK_BULLISH
    assert result.mss_confirmed is True
    assert result.confidence > 0.2
