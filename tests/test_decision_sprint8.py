from mpis.fusion.decision import (
    DecisionEngine,
    DecisionEvidence,
    DecisionSide,
)


def test_empty_evidence_holds():
    result = DecisionEngine().decide([])

    assert result.side == DecisionSide.HOLD
    assert result.confidence == 0.0


def test_strong_buy_decision():
    evidence = [
        DecisionEvidence("psychology", "BUY", 0.90),
        DecisionEvidence("liquidity", "BUY", 0.90),
        DecisionEvidence("smc", "BUY", 0.85),
        DecisionEvidence("order_flow", "BUY", 0.95),
        DecisionEvidence("confirmation", "BUY", 0.90),
    ]

    result = DecisionEngine().decide(evidence)

    assert result.side == DecisionSide.BUY
    assert result.confidence >= 0.65
    assert result.signal_quality == "STRONG"


def test_strong_sell_decision():
    evidence = [
        DecisionEvidence("psychology", "SELL", 0.90),
        DecisionEvidence("liquidity", "SELL", 0.90),
        DecisionEvidence("smc", "SELL", 0.85),
        DecisionEvidence("order_flow", "SELL", 0.95),
        DecisionEvidence("confirmation", "SELL", 0.90),
    ]

    result = DecisionEngine().decide(evidence)

    assert result.side == DecisionSide.SELL
    assert result.confidence >= 0.65


def test_conflict_forces_hold():
    evidence = [
        DecisionEvidence("psychology", "BUY", 0.90),
        DecisionEvidence("liquidity", "SELL", 0.90),
        DecisionEvidence("smc", "BUY", 0.90),
        DecisionEvidence("order_flow", "SELL", 0.90),
    ]

    result = DecisionEngine().decide(evidence)

    assert result.side == DecisionSide.HOLD
    assert result.conflict_score > 0


def test_risk_can_block_signal():
    evidence = [
        DecisionEvidence("psychology", "BUY", 0.95, risk_flag=True),
        DecisionEvidence("liquidity", "BUY", 0.95, risk_flag=True),
        DecisionEvidence("smc", "BUY", 0.95, risk_flag=True),
    ]

    result = DecisionEngine().decide(evidence)

    assert result.side == DecisionSide.HOLD
    assert result.risk_score > 0.60


def test_scores_are_clamped():
    evidence = [
        DecisionEvidence("bad_buy", "BUY", 5.0),
        DecisionEvidence("bad_sell", "SELL", -5.0),
    ]

    result = DecisionEngine().decide(evidence)

    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.bullish_score <= 1.0
    assert 0.0 <= result.bearish_score <= 1.0
    assert 0.0 <= result.risk_score <= 1.0