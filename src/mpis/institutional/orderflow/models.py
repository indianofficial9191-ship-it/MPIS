from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Side = Literal["BUY", "SELL", "NEUTRAL"]


@dataclass(frozen=True)
class OrderFlowBar:
    timestamp: datetime
    buy_pressure: float
    sell_pressure: float
    delta_proxy: float
    absorption_score: float
    imbalance_score: float
    institutional_score: float
    dominant_side: Side


@dataclass(frozen=True)
class OrderFlowSummary:
    bars_analyzed: int
    buy_pressure: float
    sell_pressure: float
    delta_proxy: float
    absorption_score: float
    imbalance_score: float
    institutional_score: float
    dominant_side: Side
