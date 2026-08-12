from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MarketSession(str, Enum):
    PRE_OPEN = "PRE_OPEN"
    REGULAR = "REGULAR"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class MarketSessionResult:
    symbol: str
    session: MarketSession
    is_open: bool
    timestamp: datetime