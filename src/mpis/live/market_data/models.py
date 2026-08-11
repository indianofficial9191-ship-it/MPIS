"""Sprint 16 normalized live market-data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MarketDataStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    exchange: str
    timestamp: datetime
    ltp: float
    volume: float = 0.0
    bid: float | None = None
    ask: float | None = None


@dataclass(frozen=True)
class MarketCandle:
    symbol: str
    exchange: str
    timestamp: datetime
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class MarketDataResult:
    status: MarketDataStatus
    accepted: bool
    reason: str = ""
    tick: MarketTick | None = None
    candle: MarketCandle | None = None
