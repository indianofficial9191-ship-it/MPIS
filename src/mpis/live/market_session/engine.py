from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from .models import MarketSession, MarketSessionResult


class MarketSessionEngine:
    """Determine NSE market session state for supported index symbols."""

    IST = ZoneInfo("Asia/Kolkata")

    SUPPORTED_SYMBOLS = frozenset({"NIFTY", "BANKNIFTY"})

    PRE_OPEN_START = time(9, 0)
    REGULAR_START = time(9, 15)
    REGULAR_END = time(15, 30)
    POST_MARKET_END = time(16, 0)

    def evaluate(
        self,
        symbol: str,
        timestamp: datetime,
    ) -> MarketSessionResult:
        symbol = symbol.upper()

        if symbol not in self.SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {symbol}")

        local_time = timestamp.astimezone(self.IST)

        if local_time.weekday() >= 5:
            session = MarketSession.CLOSED

        elif local_time.time() < self.PRE_OPEN_START:
            session = MarketSession.CLOSED

        elif local_time.time() < self.REGULAR_START:
            session = MarketSession.PRE_OPEN

        elif local_time.time() <= self.REGULAR_END:
            session = MarketSession.REGULAR

        elif local_time.time() <= self.POST_MARKET_END:
            session = MarketSession.POST_MARKET

        else:
            session = MarketSession.CLOSED

        return MarketSessionResult(
            symbol=symbol,
            session=session,
            is_open=session is MarketSession.REGULAR,
            timestamp=local_time,
        )

    def is_market_open(
        self,
        symbol: str,
        timestamp: datetime,
    ) -> bool:
        return self.evaluate(symbol, timestamp).is_open