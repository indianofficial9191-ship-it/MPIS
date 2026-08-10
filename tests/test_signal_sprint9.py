from mpis.fusion.signal import (
    SignalInput,
    SignalSide,
    UnifiedSignalEngine,
)


def test_empty_inputs_hold():
    result = UnifiedSignalEngine().generate([])

    assert result.side == SignalSide.HOLD
    assert result.confidence == 0.0


def test_aligned_buy_signal():
    inputs = [
        SignalInput("psychology", "BUY", 0.90),
        SignalInput("liquidity", "BUY", 0.85),
        SignalInput("smc", "BUY", 0.90),
        SignalInput("order_flow", "BUY", 0.95),
        SignalInput("confirmation", "BUY", 0.90),
    ]

    result = UnifiedSignalEngine().generate(inputs)

    assert result.side == SignalSide.BUY
    assert result.direction_bias == "BULLISH"
    assert result.confidence >= 0.65
    assert result.trap_warning is False


def test_aligned_sell_signal():
    inputs = [
        SignalInput("psychology", "SELL", 0.90),
        SignalInput("liquidity", "SELL", 0.85),
        SignalInput("smc", "SELL", 0.90),
        SignalInput("order_flow", "SELL", 0.95),
        SignalInput("confirmation", "SELL", 0.90),
    ]

    result = UnifiedSignalEngine().generate(inputs)

    assert result.side == SignalSide.SELL
    assert result.direction_bias == "BEARISH"
    assert result.confidence >= 0.65


def test_trap_blocks_signal():
    inputs = [
        SignalInput("psychology", "BUY", 0.95, trap_flag=True),
        SignalInput("liquidity", "BUY", 0.95),
        SignalInput("order_flow", "BUY", 0.95),
    ]

    result = UnifiedSignalEngine().generate(inputs)

    assert result.side == SignalSide.HOLD
    assert result.trap_warning is True


def test_risk_blocks_signal():
    inputs = [
        SignalInput("psychology", "BUY", 0.95, risk_flag=True),
        SignalInput("liquidity", "BUY", 0.95, risk_flag=True),
        SignalInput("smc", "BUY", 0.95, risk_flag=True),
    ]

    result = UnifiedSignalEngine().generate(inputs)

    assert result.side == SignalSide.HOLD
    assert result.risk_score > 0.60


def test_conflicting_direction_reduces_alignment():
    inputs = [
        SignalInput("psychology", "BUY", 0.90),
        SignalInput("liquidity", "SELL", 0.90),
        SignalInput("smc", "BUY", 0.80),
        SignalInput("order_flow", "SELL", 0.80),
    ]

    result = UnifiedSignalEngine().generate(inputs)

    assert result.side == SignalSide.HOLD
    assert result.alignment_score < 0.60