"""Typed models for the liquidity detection engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EqualHighResult:
    """Represents a clustered equal-high level."""

    price: float
    tolerance: float = 0.0
    strength: float = 0.0
    touch_count: int = 0
    indexes: tuple[int, ...] = field(default_factory=tuple)
    explanation: str = ""
    timestamp: datetime | None = None


@dataclass(frozen=True)
class EqualLowResult:
    """Represents a clustered equal-low level."""

    price: float
    tolerance: float = 0.0
    strength: float = 0.0
    touch_count: int = 0
    indexes: tuple[int, ...] = field(default_factory=tuple)
    explanation: str = ""
    timestamp: datetime | None = None


@dataclass(frozen=True)
class LiquidityPoolResult:
    """Represents a detected liquidity pool."""

    pool_price: float | None = None
    pool_size: int = 0
    strength: float = 0.0
    explanation: str = ""
    timestamp: datetime | None = None
    confidence: float = 0.0
    price: float | None = None
    direction: str = ""
    liquidity_level: str = ""
    touch_count: int = 0


@dataclass(frozen=True)
class StopHuntResult:
    """Represents a stop-hunt event."""

    direction: str = ""
    confidence: float = 0.0
    sweep_price: float | None = None
    rejection_price: float | None = None
    explanation: str = ""
    timestamp: datetime | None = None
    price: float | None = None


@dataclass(frozen=True)
class GrabResult:
    """Represents a liquidity grab event."""

    direction: str = ""
    confidence: float = 0.0
    sweep_price: float | None = None
    rejection_price: float | None = None
    momentum_price: float | None = None
    explanation: str = ""
    timestamp: datetime | None = None
    price: float | None = None


@dataclass(frozen=True)
class LiquidityEngineResult:
    """Aggregated output of the liquidity engine."""

    equal_highs: tuple[EqualHighResult, ...] = field(default_factory=tuple)
    equal_lows: tuple[EqualLowResult, ...] = field(default_factory=tuple)
    pools: tuple[LiquidityPoolResult, ...] = field(default_factory=tuple)
    stop_hunts: tuple[StopHuntResult, ...] = field(default_factory=tuple)
    liquidity_grabs: tuple[GrabResult, ...] = field(default_factory=tuple)


EngineResult = LiquidityEngineResult
