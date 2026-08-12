from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from mpis.live.market_session import (
    MarketSession,
    MarketSessionEngine,
)


IST = ZoneInfo("Asia/Kolkata")


def dt(hour: int, minute: int) -> datetime:
    return datetime(2026, 8, 12, hour, minute, tzinfo=IST)


def test_before_pre_open_is_closed():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(8, 59))

    assert result.session is MarketSession.CLOSED
    assert result.is_open is False


def test_pre_open_session():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(9, 5))

    assert result.session is MarketSession.PRE_OPEN
    assert result.is_open is False


def test_regular_session_at_open():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(9, 15))

    assert result.session is MarketSession.REGULAR
    assert result.is_open is True


def test_regular_session_during_market_hours():
    engine = MarketSessionEngine()

    result = engine.evaluate("BANKNIFTY", dt(12, 30))

    assert result.session is MarketSession.REGULAR
    assert result.is_open is True


def test_regular_session_at_close():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(15, 30))

    assert result.session is MarketSession.REGULAR
    assert result.is_open is True


def test_post_market_session():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(15, 45))

    assert result.session is MarketSession.POST_MARKET
    assert result.is_open is False


def test_after_post_market_is_closed():
    engine = MarketSessionEngine()

    result = engine.evaluate("NIFTY", dt(16, 1))

    assert result.session is MarketSession.CLOSED
    assert result.is_open is False


def test_weekend_is_closed():
    engine = MarketSessionEngine()

    # Saturday
    saturday = datetime(2026, 8, 15, 12, 0, tzinfo=IST)

    result = engine.evaluate("NIFTY", saturday)

    assert result.session is MarketSession.CLOSED
    assert result.is_open is False


def test_banknifty_regular_session():
    engine = MarketSessionEngine()

    result = engine.evaluate("BANKNIFTY", dt(10, 0))

    assert result.session is MarketSession.REGULAR
    assert result.is_open is True


def test_nifty_and_banknifty_are_supported():
    engine = MarketSessionEngine()

    assert engine.is_market_open("NIFTY", dt(11, 0))
    assert engine.is_market_open("BANKNIFTY", dt(11, 0))


def test_symbol_is_normalized():
    engine = MarketSessionEngine()

    result = engine.evaluate("nifty", dt(11, 0))

    assert result.symbol == "NIFTY"
    assert result.is_open is True


def test_unsupported_symbol_is_rejected():
    engine = MarketSessionEngine()

    with pytest.raises(ValueError, match="Unsupported symbol"):
        engine.evaluate("RELIANCE", dt(11, 0))


def test_result_timestamp_is_converted_to_ist():
    engine = MarketSessionEngine()

    utc = ZoneInfo("UTC")
    timestamp = datetime(2026, 8, 12, 5, 0, tzinfo=utc)

    result = engine.evaluate("NIFTY", timestamp)

    assert result.timestamp.tzinfo == IST
    assert result.timestamp.hour == 10