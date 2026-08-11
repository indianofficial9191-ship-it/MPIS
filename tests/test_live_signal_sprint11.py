from mpis.live.signal import (
    LiveSignalEngine,
    LiveSignalInput,
    LiveSignalSide,
)


def test_empty_inputs_hold():
    result = LiveSignalEngine().validate([])

    assert result.side == LiveSignalSide.HOLD
    assert result.confidence == 0.0
    assert result.quality == "NONE"


def test_aligned_buy_signal():
    inputs = [
        LiveSignalInput("psychology", "BUY", 0.90),
        LiveSignalInput("liquidity", "BUY", 0.85),
        LiveSignalInput("smc", "BUY", 0.90),
        LiveSignalInput("order_flow", "BUY", 0.95),
        LiveSignalInput("confirmation", "BUY", 0.90),
    ]

    result = LiveSignalEngine().validate(inputs)

    assert result.side == LiveSignalSide.BUY
    assert result.direction_bias == "BULLISH"
    assert result.confidence >= 0.70
    assert result.stale_warning is False


def test_aligned_sell_signal():
    inputs = [
        LiveSignalInput("psychology", "SELL", 0.90),
        LiveSignalInput("liquidity", "SELL", 0.85),
        LiveSignalInput("smc", "SELL", 0.90),
        LiveSignalInput("order_flow", "SELL", 0.95),
        LiveSignalInput("confirmation", "SELL", 0.90),
    ]

    result = LiveSignalEngine().validate(inputs)

    assert result.side == LiveSignalSide.SELL
    assert result.direction_bias == "BEARISH"
    assert result.confidence >= 0.70


def test_stale_input_blocks_live_signal():
    inputs = [
        LiveSignalInput("psychology", "BUY", 0.95),
        LiveSignalInput("liquidity", "BUY", 0.95),
        LiveSignalInput("confirmation", "BUY", 0.95, stale=True),
    ]

    result = LiveSignalEngine().validate(inputs)

    assert result.side == LiveSignalSide.HOLD
    assert result.stale_warning is True


def test_risk_blocks_live_signal():
    inputs = [
        LiveSignalInput("psychology", "BUY", 0.95, risk_flag=True),
        LiveSignalInput("liquidity", "BUY", 0.95, risk_flag=True),
        LiveSignalInput("smc", "BUY", 0.95, risk_flag=True),
    ]

    result = LiveSignalEngine().validate(inputs)

    assert result.side == LiveSignalSide.HOLD
    assert result.risk_score > 0.60


def test_conflicting_direction_reduces_alignment():
    inputs = [
        LiveSignalInput("psychology", "BUY", 0.90),
        LiveSignalInput("liquidity", "SELL", 0.90),
        LiveSignalInput("smc", "BUY", 0.80),
        LiveSignalInput("order_flow", "SELL", 0.80),
    ]

    result = LiveSignalEngine().validate(inputs)

    assert result.side == LiveSignalSide.HOLD
    assert result.alignment_score < 0.65