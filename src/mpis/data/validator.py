"""Validation utilities for MPIS market data."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import pandas as pd

from mpis.core.exceptions import DataError
from mpis.data.candle import Candle
from mpis.data.models import DataHealthStatus


@dataclass
class DataHealth:
    """Health state for the data subsystem."""

    status: DataHealthStatus = DataHealthStatus.UNKNOWN
    details: dict[str, str] = field(default_factory=dict)

    def report(self, status: DataHealthStatus, message: str | None = None) -> None:
        """Report a new health status and optional detail message."""
        self.status = status
        if message is not None:
            self.details[status.value] = message


class DataValidator:
    """Validator for candle time series and data frames."""

    def __init__(self, health: DataHealth | None = None) -> None:
        self.health = health or DataHealth()

    def validate_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Validate a pandas DataFrame before converting it to candles."""
        if dataframe.empty:
            self.health.report(DataHealthStatus.ERROR, "dataframe is empty")
            raise DataError("CSV contains no rows")

        if "timestamp" not in dataframe.columns:
            self.health.report(DataHealthStatus.ERROR, "timestamp column missing")
            raise DataError("DataFrame is missing timestamp values")

        required_columns = ["open", "high", "low", "close"]
        missing_columns = [column for column in required_columns if column not in dataframe.columns]
        if missing_columns:
            self.health.report(DataHealthStatus.ERROR, f"missing columns: {missing_columns}")
            raise DataError(f"Missing required columns: {', '.join(missing_columns)}")

        if dataframe[required_columns].isna().any().any():
            self.health.report(DataHealthStatus.ERROR, "missing OHLC values")
            raise DataError("OHLC values must not contain missing values")

        if dataframe[required_columns].lt(0.0).any().any():
            self.health.report(DataHealthStatus.ERROR, "negative price values found")
            raise DataError("OHLC values must be non-negative")

        if not dataframe["timestamp"].is_monotonic_increasing:
            self.health.report(DataHealthStatus.ERROR, "timestamp ordering is invalid")
            raise DataError("Timestamps must be ordered and unique")

        if dataframe["timestamp"].duplicated().any():
            duplicates = int(dataframe["timestamp"].duplicated().sum())
            self.health.report(DataHealthStatus.ERROR, "duplicate timestamps found")
            raise DataError(f"Duplicate timestamps found: {duplicates}")

        if (dataframe["high"] < dataframe["low"]).any():
            self.health.report(DataHealthStatus.ERROR, "high values are less than low values")
            raise DataError("Each candle high must be greater than or equal to low")

        if (dataframe["high"] < dataframe["open"]).any() or (dataframe["high"] < dataframe["close"]).any():
            self.health.report(DataHealthStatus.ERROR, "high values are less than open or close")
            raise DataError("High must be greater than or equal to open and close")

        if (dataframe["low"] > dataframe["open"]).any() or (dataframe["low"] > dataframe["close"]).any():
            self.health.report(DataHealthStatus.ERROR, "low values are greater than open or close")
            raise DataError("Low must be less than or equal to open and close")

        self.health.report(DataHealthStatus.OK, "dataframe validation succeeded")

    def validate_candles(self, candles: Sequence[Candle]) -> None:
        """Validate a sequence of candle objects."""
        if not candles:
            self.health.report(DataHealthStatus.WARNING, "buffer contains no candles")
            return

        timestamps = [candle.timestamp for candle in candles]
        if len(set(timestamps)) != len(timestamps):
            self.health.report(DataHealthStatus.ERROR, "duplicate candle timestamps detected")
            raise DataError("Duplicate candle timestamps are not allowed")

        for index in range(1, len(candles)):
            if timestamps[index] <= timestamps[index - 1]:
                self.health.report(DataHealthStatus.ERROR, "candles are not strictly ordered")
                raise DataError("Candle timestamps must increase strictly")

        for candle in candles:
            if any(math.isnan(value) for value in (candle.open, candle.high, candle.low, candle.close)):
                self.health.report(DataHealthStatus.ERROR, "NaN price value detected")
                raise DataError("Candle price values must not be NaN")

        self.health.report(DataHealthStatus.OK, "candle validation succeeded")
