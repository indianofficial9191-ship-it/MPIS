"""Sprint 17 tick-to-candle aggregation engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from mpis.live.market_data.models import MarketTick

from .models import AggregatedCandle


@dataclass
class _Bucket:
    symbol: str
    exchange: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    tick_count: int


@dataclass
class CandleAggregator:
    timeframe: str = "1m"

    _BUCKET_MINUTES = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
    }

    def __post_init__(self) -> None:
        if self.timeframe not in self._BUCKET_MINUTES:
            raise ValueError(f"Unsupported timeframe: {self.timeframe}")

        self._bucket: _Bucket | None = None
        self._last_timestamp: datetime | None = None

    @property
    def bucket_minutes(self) -> int:
        return self._BUCKET_MINUTES[self.timeframe]

    def _bucket_start(self, timestamp: datetime) -> datetime:
        minute = (
            timestamp.minute
            // self.bucket_minutes
        ) * self.bucket_minutes

        return timestamp.replace(
            minute=minute,
            second=0,
            microsecond=0,
        )

    def add_tick(self, tick: MarketTick) -> AggregatedCandle | None:
        if tick.ltp <= 0:
            raise ValueError("Tick LTP must be positive")

        if self._last_timestamp is not None:
            if tick.timestamp < self._last_timestamp:
                return None

            if tick.timestamp == self._last_timestamp:
                return None

        self._last_timestamp = tick.timestamp

        start = self._bucket_start(tick.timestamp)

        if self._bucket is None:
            self._bucket = _Bucket(
                symbol=tick.symbol,
                exchange=tick.exchange,
                timestamp=start,
                open=tick.ltp,
                high=tick.ltp,
                low=tick.ltp,
                close=tick.ltp,
                volume=max(0.0, tick.volume),
                tick_count=1,
            )
            return None

        if start != self._bucket.timestamp:
            completed = self._finalize()

            self._bucket = _Bucket(
                symbol=tick.symbol,
                exchange=tick.exchange,
                timestamp=start,
                open=tick.ltp,
                high=tick.ltp,
                low=tick.ltp,
                close=tick.ltp,
                volume=max(0.0, tick.volume),
                tick_count=1,
            )

            return completed

        self._bucket.high = max(self._bucket.high, tick.ltp)
        self._bucket.low = min(self._bucket.low, tick.ltp)
        self._bucket.close = tick.ltp
        self._bucket.volume += max(0.0, tick.volume)
        self._bucket.tick_count += 1

        return None

    def _finalize(self) -> AggregatedCandle:
        if self._bucket is None:
            raise RuntimeError("No active candle")

        bucket = self._bucket

        return AggregatedCandle(
            symbol=bucket.symbol,
            exchange=bucket.exchange,
            timeframe=self.timeframe,
            timestamp=bucket.timestamp,
            open=bucket.open,
            high=bucket.high,
            low=bucket.low,
            close=bucket.close,
            volume=bucket.volume,
            tick_count=bucket.tick_count,
        )

    def finalize(self) -> AggregatedCandle | None:
        if self._bucket is None:
            return None

        candle = self._finalize()
        self._bucket = None
        return candle
