from mpis.institutional.confirmation import (
    ConfirmationInput,
    ConfirmationSide,
    InstitutionalConfirmationEngine,
)


def test_mp_is_confirmation_pipeline_buy():
    engine = InstitutionalConfirmationEngine()

    inputs = [
        ConfirmationInput("structure", "BUY", 0.90, 1.0),
        ConfirmationInput("liquidity", "BUY", 0.85, 1.0),
        ConfirmationInput("smc", "BUY", 0.90, 1.0),
        ConfirmationInput("psychology", "BUY", 0.80, 1.0),
        ConfirmationInput("order_flow", "BUY", 0.90, 1.25),
    ]

    result = engine.analyze(inputs)

    assert result.side == ConfirmationSide.BUY
    assert result.confidence >= 0.60
    assert result.bullish_score > result.bearish_score


def test_mp_is_confirmation_pipeline_conflict():
    engine = InstitutionalConfirmationEngine()

    inputs = [
        ConfirmationInput("structure", "BUY", 0.90),
        ConfirmationInput("liquidity", "SELL", 0.90),
        ConfirmationInput("smc", "BUY", 0.80),
        ConfirmationInput("psychology", "SELL", 0.80),
        ConfirmationInput("order_flow", "SELL", 0.90),
    ]

    result = engine.analyze(inputs)

    assert result.side in {
        ConfirmationSide.HOLD,
        ConfirmationSide.SELL,
    }
    assert result.conflict_score > 0