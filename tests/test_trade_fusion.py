from datetime import datetime

from mpis.psychology.fusion import TradeFusionEngine, TradeDecision
from mpis.psychology.score import PsychologyScore, MarketBias
from mpis.psychology.models import TrendContext, TrendStrength, LiquidityGrabResult, LiquidityGrabDirection
from mpis.psychology.premium_discount import PremiumDiscountAnalysis, ZoneType
from mpis.smc.models import SMCEngineResult, ImbalanceResult, ImbalanceDirection


def test_strong_buy_all_aligned():
    psych = PsychologyScore(bullish_score=80.0, bearish_score=10.0, confidence=85.0, bias=MarketBias.STRONG_BUY, reasons=["test"])

    trend = TrendContext(
        trend=TrendStrength.VERY_BULLISH,
        confidence=0.9,
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

    engine = TradeFusionEngine()
    result = engine.analyze(psych, trend, premium, liquidity, smc)

    assert result.decision == TradeDecision.STRONG_BUY
    assert result.confidence >= 70
    assert result.reward_score >= result.risk_score
    assert any("Strong agreement" in r or "agreement" in r for r in result.reasons)


def test_strong_sell_all_aligned():
    psych = PsychologyScore(bullish_score=5.0, bearish_score=80.0, confidence=80.0, bias=MarketBias.STRONG_SELL, reasons=["test"])

    trend = TrendContext(
        trend=TrendStrength.VERY_BEARISH,
        confidence=0.85,
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

    smc = SMCEngineResult()

    engine = TradeFusionEngine()
    result = engine.analyze(psych, trend, premium, liquidity, smc)

    assert result.decision == TradeDecision.STRONG_SELL
    assert result.confidence >= 60
    assert result.risk_score >= 0


def test_conflicting_signals_hold_and_lower_confidence():
    psych = PsychologyScore(bullish_score=40.0, bearish_score=30.0, confidence=60.0, bias=MarketBias.BUY, reasons=["test"])

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

    # premium contradicts
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

    engine = TradeFusionEngine()
    result = engine.analyze(psych, trend, premium, liquidity, smc)

    assert result.decision in (TradeDecision.HOLD, TradeDecision.BUY)
    assert result.confidence < 60
    assert any("Conflicting signals" in r or "conflict" in r.lower() for r in result.reasons)


def test_neutral_hold_when_low_confidence():
    psych = PsychologyScore(bullish_score=10.0, bearish_score=10.0, confidence=10.0, bias=MarketBias.NEUTRAL, reasons=["test"])

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

    engine = TradeFusionEngine()
    result = engine.analyze(psych, trend, premium, liquidity, smc)

    assert result.decision == TradeDecision.HOLD
    assert result.confidence < 30
    assert result.risk_score >= 0
    assert "Low confidence" in " ".join(result.reasons)
