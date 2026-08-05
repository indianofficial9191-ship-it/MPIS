from datetime import datetime

from mpis.psychology.models import (
    TrendContext,
    TrendStrength,
    LiquidityGrabResult,
    LiquidityGrabDirection,
)
from mpis.psychology.premium_discount import PremiumDiscountAnalysis, ZoneType
from mpis.smc.models import SMCEngineResult, ImbalanceResult, ImbalanceDirection
from mpis.psychology.score import PsychologyScoreEngine, MarketBias


def test_strong_buy_with_very_bullish_trend_and_discount_and_liquidity_smc():
    trend = TrendContext(
        trend=TrendStrength.VERY_BULLISH,
        confidence=0.8,
        bos_confirmed=True,
        choch_confirmed=False,
        mss_confirmed=True,
        swing_highs=[15000.0],
        swing_lows=[14800.0],
        timestamp=datetime.utcnow(),
    )

    premium = PremiumDiscountAnalysis(
        current_price=14900.0,
        swing_high=15000.0,
        swing_low=14800.0,
        equilibrium=14900.0,
        zone=ZoneType.DISCOUNT,
        premium_percent=50.0,
        discount_percent=50.0,
    )

    liquidity = LiquidityGrabResult(
        found=True,
        direction=LiquidityGrabDirection.BULLISH,
        confidence=0.8,
        sweep_price=14750.0,
        rejection_price=14850.0,
        close_back_inside=True,
        explanation="bullish sweep",
    )

    smc = SMCEngineResult(imbalances=(ImbalanceResult(direction=ImbalanceDirection.BULLISH, body_ratio=0.5, range_ratio=0.6, momentum_score=0.7, timestamp=datetime.utcnow()),))

    engine = PsychologyScoreEngine()
    score = engine.analyze(trend, premium, liquidity, smc)

    assert score.bias == MarketBias.STRONG_BUY
    assert score.bullish_score > score.bearish_score
    assert score.confidence >= 60
    assert any("Trend" in r for r in score.reasons)
    assert any("Discount" in r or "Discount".lower() for r in score.reasons)


def test_strong_sell_with_very_bearish_trend_and_premium():
    trend = TrendContext(
        trend=TrendStrength.VERY_BEARISH,
        confidence=0.7,
        bos_confirmed=True,
        choch_confirmed=False,
        mss_confirmed=True,
        swing_highs=[35000.0],
        swing_lows=[34800.0],
        timestamp=datetime.utcnow(),
    )

    premium = PremiumDiscountAnalysis(
        current_price=34950.0,
        swing_high=35000.0,
        swing_low=34800.0,
        equilibrium=34900.0,
        zone=ZoneType.PREMIUM,
        premium_percent=60.0,
        discount_percent=40.0,
    )

    liquidity = LiquidityGrabResult(
        found=True,
        direction=LiquidityGrabDirection.BEARISH,
        confidence=0.9,
        sweep_price=35050.0,
        rejection_price=34950.0,
        close_back_inside=True,
        explanation="bearish sweep",
    )

    smc = SMCEngineResult()  # empty smc

    engine = PsychologyScoreEngine()
    score = engine.analyze(trend, premium, liquidity, smc)

    assert score.bias == MarketBias.STRONG_SELL
    assert score.bearish_score > score.bullish_score
    assert score.confidence >= 50


def test_conflicting_signals_reduce_confidence():
    trend = TrendContext(
        trend=TrendStrength.BULLISH,
        confidence=0.6,
        bos_confirmed=True,
        choch_confirmed=False,
        mss_confirmed=False,
        swing_highs=[12000.0],
        swing_lows=[11800.0],
        timestamp=datetime.utcnow(),
    )

    # premium contradicts bullish trend
    premium = PremiumDiscountAnalysis(
        current_price=11950.0,
        swing_high=12000.0,
        swing_low=11800.0,
        equilibrium=11900.0,
        zone=ZoneType.PREMIUM,
        premium_percent=55.0,
        discount_percent=45.0,
    )

    liquidity = None
    smc = None

    engine = PsychologyScoreEngine()
    score = engine.analyze(trend, premium, liquidity, smc)

    # base confidence from trend = 60, but conflict penalty applied
    assert score.confidence < 60
    assert score.bias in (MarketBias.BUY, MarketBias.NEUTRAL)


def test_neutral_sideways_equilibrium_no_inputs():
    trend = TrendContext(
        trend=TrendStrength.SIDEWAYS,
        confidence=0.1,
        bos_confirmed=False,
        choch_confirmed=False,
        mss_confirmed=False,
        swing_highs=[],
        swing_lows=[],
        timestamp=datetime.utcnow(),
    )

    premium = PremiumDiscountAnalysis(
        current_price=100.0,
        swing_high=100.0,
        swing_low=100.0,
        equilibrium=100.0,
        zone=ZoneType.EQUILIBRIUM,
        premium_percent=0.0,
        discount_percent=0.0,
    )

    liquidity = None
    smc = SMCEngineResult()

    engine = PsychologyScoreEngine()
    score = engine.analyze(trend, premium, liquidity, smc)

    assert score.bias == MarketBias.NEUTRAL
    assert score.confidence >= 0
    assert isinstance(score.reasons, list)
