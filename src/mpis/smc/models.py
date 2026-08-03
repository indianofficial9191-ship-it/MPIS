"""Typed dataclasses for the Smart Money Concepts engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class FVGDirection(str, Enum):
    """Direction of a fair value gap."""

    BULLISH = "bullish"
    BEARISH = "bearish"


class FVGStatus(str, Enum):
    """Lifecycle status of a fair value gap."""

    ACTIVE = "active"
    FILLED = "filled"


@dataclass(frozen=True)
class FVGResult:
    """Represents a fair value gap."""

    direction: FVGDirection
    gap_size: float
    fill_percentage: float
    status: FVGStatus
    strength: float
    timestamp: datetime
    low: float
    high: float


class ImbalanceDirection(str, Enum):
    """Direction of a displacement imbalance."""

    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class ImbalanceResult:
    """Represents a displacement imbalance candle."""

    direction: ImbalanceDirection
    body_ratio: float
    range_ratio: float
    momentum_score: float
    timestamp: datetime


class OrderBlockDirection(str, Enum):
    """Direction of an order block."""

    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class OrderBlockResult:
    """Represents an order block."""

    direction: OrderBlockDirection
    high: float
    low: float
    strength: float
    freshness: int
    retest_count: int
    validity: str
    timestamp: datetime
    origin_candle: datetime | None = None


class BreakerBlockDirection(str, Enum):
    """Direction of a breaker block."""

    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class BreakerBlockResult:
    """Represents an invalidated order block turned breaker block."""

    direction: BreakerBlockDirection
    strength: float
    origin_block: dict[str, object]
    timestamp: datetime


class MitigationStatus(str, Enum):
    """Status of a mitigation block revisit."""

    PARTIAL = "partial"
    FULL = "full"


@dataclass(frozen=True)
class MitigationBlockResult:
    """Represents a mitigation block revisit."""

    status: MitigationStatus
    strength_score: float
    reference_price: float
    timestamp: datetime


@dataclass(frozen=True)
class SMCEngineResult:
    """Aggregated output of the SMC engine."""

    fvgs: tuple[FVGResult, ...] = field(default_factory=tuple)
    imbalances: tuple[ImbalanceResult, ...] = field(default_factory=tuple)
    order_blocks: tuple[OrderBlockResult, ...] = field(default_factory=tuple)
    breaker_blocks: tuple[BreakerBlockResult, ...] = field(default_factory=tuple)
    mitigation_blocks: tuple[MitigationBlockResult, ...] = field(default_factory=tuple)
