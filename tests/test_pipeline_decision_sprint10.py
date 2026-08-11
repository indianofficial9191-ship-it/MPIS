from mpis.pipeline.decision import (
    PipelineDecisionEngine,
    PipelineDecisionInput,
    PipelineDecisionSide,
)


def test_empty_inputs_hold():
    result = PipelineDecisionEngine().decide([])

    assert result.side == PipelineDecisionSide.HOLD
    assert result.confidence == 0.0
    assert result.quality == "NONE"


def test_aligned_buy_decision():
    inputs = [
        PipelineDecisionInput("psychology", "BUY", 0.90),
        PipelineDecisionInput("liquidity", "BUY", 0.85),
        PipelineDecisionInput("smc", "BUY", 0.90),
        PipelineDecisionInput("order_flow", "BUY", 0.95),
        PipelineDecisionInput("confirmation", "BUY", 0.90),
    ]

    result = PipelineDecisionEngine().decide(inputs)

    assert result.side == PipelineDecisionSide.BUY
    assert result.direction_bias == "BULLISH"
    assert result.confidence >= 0.70
    assert result.alignment_score >= 0.65
    assert result.trap_warning is False


def test_aligned_sell_decision():
    inputs = [
        PipelineDecisionInput("psychology", "SELL", 0.90),
        PipelineDecisionInput("liquidity", "SELL", 0.85),
        PipelineDecisionInput("smc", "SELL", 0.90),
        PipelineDecisionInput("order_flow", "SELL", 0.95),
        PipelineDecisionInput("confirmation", "SELL", 0.90),
    ]

    result = PipelineDecisionEngine().decide(inputs)

    assert result.side == PipelineDecisionSide.SELL
    assert result.direction_bias == "BEARISH"
    assert result.confidence >= 0.70


def test_trap_blocks_decision():
    inputs = [
        PipelineDecisionInput("psychology", "BUY", 0.95, trap_flag=True),
        PipelineDecisionInput("liquidity", "BUY", 0.95),
        PipelineDecisionInput("order_flow", "BUY", 0.95),
    ]

    result = PipelineDecisionEngine().decide(inputs)

    assert result.side == PipelineDecisionSide.HOLD
    assert result.trap_warning is True


def test_high_risk_blocks_decision():
    inputs = [
        PipelineDecisionInput("psychology", "BUY", 0.95, risk_flag=True),
        PipelineDecisionInput("liquidity", "BUY", 0.95, risk_flag=True),
        PipelineDecisionInput("smc", "BUY", 0.95, risk_flag=True),
    ]

    result = PipelineDecisionEngine().decide(inputs)

    assert result.side == PipelineDecisionSide.HOLD
    assert result.risk_score > 0.60


def test_conflicting_inputs_reduce_alignment():
    inputs = [
        PipelineDecisionInput("psychology", "BUY", 0.90),
        PipelineDecisionInput("liquidity", "SELL", 0.90),
        PipelineDecisionInput("smc", "BUY", 0.80),
        PipelineDecisionInput("order_flow", "SELL", 0.80),
    ]

    result = PipelineDecisionEngine().decide(inputs)

    assert result.side == PipelineDecisionSide.HOLD
    assert result.alignment_score < 0.65
