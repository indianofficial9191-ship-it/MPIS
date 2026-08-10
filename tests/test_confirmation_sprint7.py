from mpis.institutional.confirmation import (
    ConfirmationInput,
    ConfirmationSide,
    InstitutionalConfirmationEngine,
)


def test_empty_inputs_hold():
    result = InstitutionalConfirmationEngine().analyze([])

    assert result.side == ConfirmationSide.HOLD
    assert result.confidence == 0.0


def test_strong_buy_alignment():
    inputs = [
        ConfirmationInput("structure", "BUY", 0.90),
        ConfirmationInput("liquidity", "BUY", 0.85),
        ConfirmationInput("smc", "BUY", 0.90),
        ConfirmationInput("psychology", "BUY", 0.80),
        ConfirmationInput("order_flow", "BUY", 0.90),
    ]

    result = InstitutionalConfirmationEngine().analyze(inputs)

    assert result.side == ConfirmationSide.BUY
    assert result.bullish_score > result.bearish_score
    assert result.confidence >= 0.60


def test_strong_sell_alignment():
    inputs = [
        ConfirmationInput("structure", "SELL", 0.90),
        ConfirmationInput("liquidity", "SELL", 0.85),
        ConfirmationInput("smc", "SELL", 0.90),
        ConfirmationInput("psychology", "SELL", 0.80),
        ConfirmationInput("order_flow", "SELL", 0.90),
    ]

    result = InstitutionalConfirmationEngine().analyze(inputs)

    assert result.side == ConfirmationSide.SELL
    assert result.bearish_score > result.bullish_score
    assert result.confidence >= 0.60


def test_conflicting_evidence_produces_hold():
    inputs = [
        ConfirmationInput("structure", "BUY", 0.90),
        ConfirmationInput("liquidity", "SELL", 0.90),
        ConfirmationInput("smc", "BUY", 0.80),
        ConfirmationInput("psychology", "SELL", 0.80),
    ]

    result = InstitutionalConfirmationEngine().analyze(inputs)

    assert result.side == ConfirmationSide.HOLD
    assert result.conflict_score > 0
    assert result.confidence < 0.60


def test_scores_are_clamped():
    inputs = [
        ConfirmationInput("structure", "BUY", 5.0),
        ConfirmationInput("order_flow", "SELL", -5.0),
    ]

    result = InstitutionalConfirmationEngine().analyze(inputs)

    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.bullish_score <= 1.0
    assert 0.0 <= result.bearish_score <= 1.0