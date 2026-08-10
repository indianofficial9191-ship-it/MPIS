from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import numpy as np
import pandas as pd

from .models import OrderFlowBar, OrderFlowSummary


@dataclass(frozen=True)
class OrderFlowAnalyzer:
    """
    OHLCV-based institutional order-flow proxy.

    Important: OHLCV cannot reveal the true bid/ask aggressor or order book.
    This engine therefore estimates pressure from candle structure + volume.
    It is deliberately designed so real tick/order-book data can replace the
    proxy inputs later without changing the result model.
    """

    volume_window: int = 20
    imbalance_threshold: float = 0.25
    absorption_threshold: float = 0.65

    def analyze(self, frame: pd.DataFrame) -> OrderFlowSummary:
        bars = list(self.analyze_bars(frame))
        if not bars:
            return OrderFlowSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "NEUTRAL")

        mean = lambda attr: float(np.mean([getattr(b, attr) for b in bars]))
        delta = mean("delta_proxy")
        buy = mean("buy_pressure")
        sell = mean("sell_pressure")
        absorption = mean("absorption_score")
        imbalance = mean("imbalance_score")
        institutional = mean("institutional_score")

        if delta > self.imbalance_threshold:
            side = "BUY"
        elif delta < -self.imbalance_threshold:
            side = "SELL"
        else:
            side = "NEUTRAL"

        return OrderFlowSummary(
            bars_analyzed=len(bars),
            buy_pressure=buy,
            sell_pressure=sell,
            delta_proxy=delta,
            absorption_score=absorption,
            imbalance_score=imbalance,
            institutional_score=institutional,
            dominant_side=side,
        )

    def analyze_bars(self, frame: pd.DataFrame) -> Iterable[OrderFlowBar]:
        self._validate(frame)
        df = frame.copy()

        numeric = ["open", "high", "low", "close", "volume"]
        for col in numeric:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=numeric)
        if df.empty:
            return []

        rolling_volume = (
            df["volume"].rolling(self.volume_window, min_periods=1).median()
        )

        result: list[OrderFlowBar] = []
        for idx, row in df.iterrows():
            o, h, l, c, v = map(float, row[numeric])
            rng = max(h - l, 1e-12)
            body = abs(c - o) / rng
            close_location = ((c - l) / rng) * 2.0 - 1.0
            wick_upper = max(h - max(o, c), 0.0) / rng
            wick_lower = max(min(o, c) - l, 0.0) / rng

            median_volume = max(float(rolling_volume.loc[idx]), 1e-12)
            volume_factor = min(v / median_volume, 3.0) / 3.0

            directional = np.clip(close_location * (0.35 + 0.65 * body), -1.0, 1.0)
            buy_pressure = float(np.clip((directional + 1.0) / 2.0, 0.0, 1.0))
            sell_pressure = 1.0 - buy_pressure
            delta_proxy = float(directional * volume_factor)

            # Absorption proxy: high relative volume with a small body and
            # meaningful opposing wick. This is not a true footprint reading.
            opposing_wick = max(wick_upper, wick_lower)
            absorption = float(
                np.clip(volume_factor * (1.0 - body) * opposing_wick, 0.0, 1.0)
            )

            imbalance = float(np.clip(abs(delta_proxy), 0.0, 1.0))
            institutional = float(
                np.clip(
                    0.45 * imbalance
                    + 0.35 * absorption
                    + 0.20 * volume_factor,
                    0.0,
                    1.0,
                )
            )

            if delta_proxy > self.imbalance_threshold:
                side = "BUY"
            elif delta_proxy < -self.imbalance_threshold:
                side = "SELL"
            else:
                side = "NEUTRAL"

            timestamp = self._timestamp(row, idx)
            result.append(
                OrderFlowBar(
                    timestamp=timestamp,
                    buy_pressure=buy_pressure,
                    sell_pressure=float(sell_pressure),
                    delta_proxy=delta_proxy,
                    absorption_score=absorption,
                    imbalance_score=imbalance,
                    institutional_score=institutional,
                    dominant_side=side,
                )
            )

        return result

    @staticmethod
    def _validate(frame: pd.DataFrame) -> None:
        required = {"open", "high", "low", "close", "volume"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(
                "Missing required OHLCV columns: " + ", ".join(sorted(missing))
            )

    @staticmethod
    def _timestamp(row: pd.Series, fallback: object) -> datetime:
        if "timestamp" in row.index:
            value = pd.to_datetime(row["timestamp"], errors="coerce")
            if not pd.isna(value):
                return value.to_pydatetime()
        if isinstance(fallback, (pd.Timestamp, datetime)):
            return pd.Timestamp(fallback).to_pydatetime()
        return datetime.fromtimestamp(0)
