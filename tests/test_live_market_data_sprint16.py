from datetime import datetime

from mpis.live.market_data import (
    MarketCandle,
    MarketDataGateway,
    MarketDataStatus,
    MarketTick,
)


def test_valid_tick_is_healthy():
    tick = MarketTick(
        "NIFTY",
        "NSE",
        datetime.now(),
        25000.0,
        volume=1000,
        bid=24999.5,
        ask=25000.5,
    )

    result = MarketDataGateway().validate_tick(tick)

    assert result.status == MarketDataStatus.HEALTHY
    assert result.accepted is True


def test_unsupported_symbol_is_rejected():
    tick = MarketTick(
        "RELIANCE",
        "NSE",
        datetime.now(),
        1500.0,
    )

    result = MarketDataGateway().validate_tick(tick)

    assert result.status == MarketDataStatus.INVALID
    assert result.accepted is False


def test_invalid_ltp_is_rejected():
    tick = MarketTick(
        "NIFTY",
        "NSE",
        datetime.now(),
        0.0,
    )

    result = MarketDataGateway().validate_tick(tick)

    assert result.reason == "INVALID_LTP"


def test_crossed_market_is_rejected():
    tick = MarketTick(
        "BANKNIFTY",
        "NSE",
        datetime.now(),
        50000.0,
        bid=50010.0,
        ask=49990.0,
    )

    result = MarketDataGateway().validate_tick(tick)

    assert result.reason == "CROSSED_MARKET"


def test_valid_candle_is_healthy():
    candle = MarketCandle(
        "NIFTY",
        "NSE",
        datetime.now(),
        "1m",
        25000.0,
        25020.0,
        24990.0,
        25010.0,
        volume=5000,
    )

    result = MarketDataGateway().validate_candle(candle)

    assert result.status == MarketDataStatus.HEALTHY
    assert result.accepted is True


def test_invalid_candle_ohlc_is_rejected():
    candle = MarketCandle(
        "NIFTY",
        "NSE",
        datetime.now(),
        "1m",
        25000.0,
        24990.0,
        24980.0,
        25010.0,
    )

    result = MarketDataGateway().validate_candle(candle)

    assert result.status == MarketDataStatus.INVALID
    assert result.reason == "HIGH_BELOW_BODY"


def test_unsupported_timeframe_is_rejected():
    candle = MarketCandle(
        "BANKNIFTY",
        "NSE",
        datetime.now(),
        "2h",
        50000.0,
        50100.0,
        49900.0,
        50050.0,
    )

    result = MarketDataGateway().validate_candle(candle)

    assert result.reason == "UNSUPPORTED_TIMEFRAME"
