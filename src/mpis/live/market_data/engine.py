"""Sprint 16 normalized live market-data gateway."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import (
    MarketCandle,
    MarketDataResult,
    MarketDataStatus,
    MarketTick,
)


@dataclass(frozen=True)
class MarketDataGateway:
    allowed_symbols: tuple[str, ...] = ("NIFTY", "BANKNIFTY")

    def validate_tick(self, tick: MarketTick) -> MarketDataResult:
        if tick.symbol.upper() not in self.allowed_symbols:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="UNSUPPORTED_SYMBOL",
                tick=tick,
            )

        if not tick.exchange.strip():
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="MISSING_EXCHANGE",
                tick=tick,
            )

        if not isinstance(tick.timestamp, datetime):
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_TIMESTAMP",
                tick=tick,
            )

        if tick.ltp <= 0:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_LTP",
                tick=tick,
            )

        if tick.volume < 0:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_VOLUME",
                tick=tick,
            )

        if tick.bid is not None and tick.bid <= 0:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_BID",
                tick=tick,
            )

        if tick.ask is not None and tick.ask <= 0:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_ASK",
                tick=tick,
            )

        if tick.bid is not None and tick.ask is not None and tick.bid > tick.ask:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="CROSSED_MARKET",
                tick=tick,
            )

        return MarketDataResult(
            status=MarketDataStatus.HEALTHY,
            accepted=True,
            reason="VALID_TICK",
            tick=tick,
        )

    def validate_candle(self, candle: MarketCandle) -> MarketDataResult:
        if candle.symbol.upper() not in self.allowed_symbols:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="UNSUPPORTED_SYMBOL",
                candle=candle,
            )

        if not candle.exchange.strip():
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="MISSING_EXCHANGE",
                candle=candle,
            )

        if not isinstance(candle.timestamp, datetime):
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_TIMESTAMP",
                candle=candle,
            )

        if candle.timeframe not in {"1m", "5m", "15m", "30m", "1h"}:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="UNSUPPORTED_TIMEFRAME",
                candle=candle,
            )

        prices = (
            candle.open,
            candle.high,
            candle.low,
            candle.close,
        )

        if any(price <= 0 for price in prices):
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_PRICE",
                candle=candle,
            )

        if candle.high < max(candle.open, candle.close):
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="HIGH_BELOW_BODY",
                candle=candle,
            )

        if candle.low > min(candle.open, candle.close):
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="LOW_ABOVE_BODY",
                candle=candle,
            )

        if candle.high < candle.low:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="HIGH_BELOW_LOW",
                candle=candle,
            )

        if candle.volume < 0:
            return MarketDataResult(
                status=MarketDataStatus.INVALID,
                accepted=False,
                reason="INVALID_VOLUME",
                candle=candle,
            )

        return MarketDataResult(
            status=MarketDataStatus.HEALTHY,
            accepted=True,
            reason="VALID_CANDLE",
            candle=candle,
        )
