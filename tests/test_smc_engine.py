from datetime import datetime

from mpis.data.candle import Candle
from mpis.smc import SMCEngine, SMCEngineResult


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_smc_engine_returns_all_component_results() -> None:
    candles = [
        _candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.5, 99.5, 100.2),
        _candle(datetime(2026, 8, 3, 9, 1), 101.2, 101.8, 100.8, 101.5),
        _candle(datetime(2026, 8, 3, 9, 2), 100.0, 100.3, 99.6, 100.1),
        _candle(datetime(2026, 8, 3, 9, 3), 100.4, 101.2, 100.2, 101.0),
        _candle(datetime(2026, 8, 3, 9, 4), 100.0, 100.4, 99.8, 100.1),
    ]
    engine = SMCEngine()

    result = engine.analyze(candles)

    assert isinstance(result, SMCEngineResult)
    assert len(result.fvgs) >= 0
    assert len(result.imbalances) >= 0
    assert len(result.order_blocks) >= 0
    assert len(result.breaker_blocks) >= 0
    assert len(result.mitigation_blocks) >= 0


def test_smc_engine_handles_short_buffer() -> None:
    engine = SMCEngine()

    result = engine.analyze([_candle(datetime(2026, 8, 3, 9, 0), 100.0, 100.1, 99.9, 100.0)])

    assert isinstance(result, SMCEngineResult)
    assert result.fvgs == ()
    assert result.imbalances == ()
    assert result.order_blocks == ()
    assert result.breaker_blocks == ()
    assert result.mitigation_blocks == ()
