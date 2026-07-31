"""Candle model for MPIS market data."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from mpis.core.exceptions import ValidationError


@dataclass(frozen=True)
class Candle:
    """Immutable candle model for market data replay."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    symbol: str
    timeframe: str
    volume: float | None = None
    oi: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise ValidationError("timestamp must be a datetime instance")
        if self.high < self.low:
            raise ValidationError("high must be greater than or equal to low")
        if self.high < self.open:
            raise ValidationError("high must be greater than or equal to open")
        if self.high < self.close:
            raise ValidationError("high must be greater than or equal to close")
        if self.low > self.open:
            raise ValidationError("low must be less than or equal to open")
        if self.low > self.close:
            raise ValidationError("low must be less than or equal to close")
        if self.open < 0.0 or self.high < 0.0 or self.low < 0.0 or self.close < 0.0:
            raise ValidationError("price values must be non-negative")
        if self.volume is not None and self.volume < 0.0:
            raise ValidationError("volume must be non-negative")
        if self.oi is not None and self.oi < 0.0:
            raise ValidationError("oi must be non-negative")
        if not self.symbol:
            raise ValidationError("symbol must be provided")
        if not self.timeframe:
            raise ValidationError("timeframe must be provided")

    @property
    def bullish(self) -> bool:
        """Return True when the candle closes higher than it opens."""
        return self.close > self.open

    @property
    def bearish(self) -> bool:
        """Return True when the candle closes lower than it opens."""
        return self.open > self.close

    @property
    def body(self) -> float:
        """Return the absolute body size of the candle."""
        return abs(self.close - self.open)

    @property
    def upper_wick(self) -> float:
        """Return the upper wick length of the candle."""
        return max(self.high - max(self.open, self.close), 0.0)

    @property
    def lower_wick(self) -> float:
        """Return the lower wick length of the candle."""
        return max(min(self.open, self.close) - self.low, 0.0)

    @property
    def range(self) -> float:
        """Return the full high-low range of the candle."""
        return self.high - self.low

    @property
    def typical_price(self) -> float:
        """Return the typical price for the candle."""
        return (self.high + self.low + self.close) / 3.0

    @property
    def median_price(self) -> float:
        """Return the median of high and low."""
        return (self.high + self.low) / 2.0

    @property
    def weighted_price(self) -> float:
        """Return a weighted price emphasizing the close."""
        return (self.high + self.low + self.close * 2.0) / 4.0
