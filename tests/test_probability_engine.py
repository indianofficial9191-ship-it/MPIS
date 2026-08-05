from mpis.psychology.probability import ProbabilityEngine, ProbabilityResult, RiskLevel
from mpis.psychology.fusion import TradeFusionResult, TradeDecision


def test_high_confidence_allows_trade():
    fusion = TradeFusionResult(
        decision=TradeDecision.STRONG_BUY,
        confidence=80.0,
        risk_score=10.0,
        reward_score=70.0,
        reasons=["test"],
    )

    engine = ProbabilityEngine(minimum_trade_probability=50.0)
    result = engine.analyze(fusion)

    # probability = 80 + (70-10)*0.25 = 80 + 15 = 95
    assert isinstance(result, ProbabilityResult)
    assert result.probability >= 90
    assert result.trade_allowed is True
    assert result.risk_level == RiskLevel.LOW


def test_low_confidence_denies_trade():
    fusion = TradeFusionResult(
        decision=TradeDecision.SELL,
        confidence=20.0,
        risk_score=60.0,
        reward_score=30.0,
        reasons=["test"],
    )

    engine = ProbabilityEngine(minimum_trade_probability=40.0)
    result = engine.analyze(fusion)

    # probability = 20 + (30-60)*0.25 = 20 - 7.5 = 12.5
    assert result.probability <= 20
    assert result.trade_allowed is False
    assert result.risk_level == RiskLevel.MEDIUM


def test_threshold_boundary_allows_when_equal():
    # Construct fusion so probability becomes exactly 90 using formula
    # confidence 85 + (70-50)*0.25 = 85 + 5 = 90
    fusion = TradeFusionResult(
        decision=TradeDecision.BUY,
        confidence=85.0,
        risk_score=50.0,
        reward_score=70.0,
        reasons=["test"],
    )

    engine = ProbabilityEngine(minimum_trade_probability=90.0)
    result = engine.analyze(fusion)

    assert result.probability == 90.0
    assert result.trade_allowed is True
    assert result.decision == TradeDecision.BUY
