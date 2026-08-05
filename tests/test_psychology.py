from datetime import datetime

import pytest

from mpis.psychology.engine import PsychologyEngine
from mpis.psychology.models import TrendContext, TrendStrength
from mpis.psychology.score import PsychologyScore, MarketBias


def test_compute_probability_with_both_inputs():
    trend = TrendContext(
        trend=TrendStrength.BULLISH,
        confidence=0.8,
        bos_confirmed=True,
        choch_confirmed=False,
        mss_confirmed=True,
        swing_highs=[150.0],
        swing_lows=[145.0],
        timestamp=datetime.utcnow(),
    )

    psychology = PsychologyScore(
        bullish_score=40.0,
        bearish_score=10.0,
        confidence=70.0,
        bias=MarketBias.BUY,
        reasons=["unit-test"],
    )

    engine = PsychologyEngine()
    out = engine.compute_probability(trend=trend, psychology=psychology)

    # Calculations:
    # trend_pct = 0.8 * 100 = 80
    # psych_pct = 70
    # confidence = mean(80,70)=75
    # probability = trend*0.6 + psych*0.4 = 80*0.6 + 70*0.4 = 76
    assert out.direction == "buy"
    assert out.confidence == 75.0
    assert out.probability == 76.0
    assert isinstance(out.reasons, list) and len(out.reasons) >= 3


def test_compute_probability_with_only_trend():
    trend = TrendContext(
        trend=TrendStrength.VERY_BULLISH,
        confidence=0.5,
        bos_confirmed=False,
        choch_confirmed=False,
        mss_confirmed=False,
        swing_highs=[],
        swing_lows=[],
        timestamp=datetime.utcnow(),
    )

    engine = PsychologyEngine()
    out = engine.compute_probability(trend=trend, psychology=None)

    # trend_pct = 50, psych_pct = 0
    # confidence = 25.0
    # probability = 50*0.6 + 0*0.4 = 30.0
    assert out.direction == "buy"
    assert out.confidence == 25.0
    assert out.probability == 30.0


def test_compute_probability_with_only_psychology():
    psychology = PsychologyScore(
        bullish_score=5.0,
        bearish_score=60.0,
        confidence=60.0,
        bias=MarketBias.STRONG_SELL,
        reasons=["unit"],
    )

    engine = PsychologyEngine()
    out = engine.compute_probability(trend=None, psychology=psychology)

    # trend_pct = 0, psych_pct = 60
    # confidence = 30.0
    # probability = 0*0.6 + 60*0.4 = 24.0
    assert out.direction == "sell"
    assert out.confidence == 30.0
    assert out.probability == 24.0


def test_weights_validation():
    with pytest.raises(ValueError):
        PsychologyEngine(trend_weight=0.7, psychology_weight=0.4)

    with pytest.raises(ValueError):
        PsychologyEngine(trend_weight=1.1, psychology_weight=-0.1)


def test_clamping_of_values():
    # provide out-of-range confidences to ensure clamping
    trend = TrendContext(
        trend=TrendStrength.BEARISH,
        confidence=2.0,  # 200%
        bos_confirmed=False,
        choch_confirmed=False,
        mss_confirmed=False,
        swing_highs=[],
        swing_lows=[],
        timestamp=datetime.utcnow(),
    )

    psychology = PsychologyScore(
        bullish_score=0.0,
        bearish_score=0.0,
        confidence=250.0,  # 250%
        bias=MarketBias.NEUTRAL,
        reasons=[],
    )

    engine = PsychologyEngine()
    out = engine.compute_probability(trend=trend, psychology=psychology)

    # trend_pct = 200 => clamped later to 100 in final values
    # psych_pct = 250 => clamped to 100
    assert 0.0 <= out.confidence <= 100.0
    assert 0.0 <= out.probability <= 100.0
    assert out.direction in ("buy", "sell", "neutral")
