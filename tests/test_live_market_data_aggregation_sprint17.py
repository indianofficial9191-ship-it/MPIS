from datetime import datetime, timedelta

from mpis.live.market_data import MarketTick
from mpis.live.market_data.aggregation import CandleAggregator


def make_tick(timestamp, price, volume=10):
    return MarketTick(
        symbol="NIFTY",
        exchange="NSE",
        timestamp=timestamp,
        ltp=price,
        volume=volume,
    )


def test_one_minute_candle_aggregation():
    start = datetime(2026, 1, 1, 9, 15, 10)

    aggregator = CandleAggregator("1m")

    assert aggregator.add_tick(
        make_tick(start, 100.0)
    ) is None

    assert aggregator.add_tick(
        make_tick(start + timedelta(seconds=20), 105.0)
    ) is None

    result = aggregator.add_tick(
        make_tick(start + timedelta(minutes=1), 103.0)
    )

    assert result is not None
    assert result.open == 100.0
    assert result.high == 105.0
    assert result.low == 100.0
    assert result.close == 105.0
    assert result.volume == 20
    assert result.tick_count == 2


def test_five_minute_bucket():
    start = datetime(2026, 1, 1, 9, 16, 10)

    aggregator = CandleAggregator("5m")

    aggregator.add_tick(make_tick(start, 100.0))
    aggregator.add_tick(
        make_tick(start + timedelta(minutes=3), 110.0)
    )

    result = aggregator.add_tick(
        make_tick(start + timedelta(minutes=5), 108.0)
    )

    assert result is not None
    assert result.timeframe == "5m"
    assert result.open == 100.0
    assert result.high == 110.0
    assert result.close == 110.0


def test_fifteen_minute_bucket():
    start = datetime(2026, 1, 1, 9, 16)

    aggregator = CandleAggregator("15m")

    aggregator.add_tick(make_tick(start, 100.0))
    aggregator.add_tick(
        make_tick(start + timedelta(minutes=10), 120.0)
    )

    result = aggregator.add_tick(
        make_tick(start + timedelta(minutes=15), 115.0)
    )

    assert result is not None
    assert result.timeframe == "15m"
    assert result.high == 120.0


def test_out_of_order_tick_is_ignored():
    start = datetime(2026, 1, 1, 9, 15)

    aggregator = CandleAggregator("1m")

    aggregator.add_tick(make_tick(start, 100.0))

    result = aggregator.add_tick(
        make_tick(start - timedelta(seconds=1), 95.0)
    )

    assert result is None

    final = aggregator.finalize()

    assert final is not None
    assert final.close == 100.0


def test_duplicate_timestamp_is_ignored():
    start = datetime(2026, 1, 1, 9, 15)

    aggregator = CandleAggregator("1m")

    aggregator.add_tick(make_tick(start, 100.0))
    aggregator.add_tick(make_tick(start, 110.0))

    final = aggregator.finalize()

    assert final is not None
    assert final.close == 100.0
    assert final.tick_count == 1


def test_finalize_returns_current_candle():
    start = datetime(2026, 1, 1, 9, 15)

    aggregator = CandleAggregator("1m")
    aggregator.add_tick(make_tick(start, 100.0))

    result = aggregator.finalize()

    assert result is not None
    assert result.open == 100.0
    assert result.close == 100.0

    assert aggregator.finalize() is None


def test_invalid_timeframe_is_rejected():
    try:
        CandleAggregator("2h")
    except ValueError:
        return

    raise AssertionError("Expected unsupported timeframe to fail")
