"""Break-of-structure detection for MPIS market analysis."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from mpis.data.candle import Candle
from mpis.structure.models import StructureSignal, StructureType, TrendState


class BreakOfStructureType(str, Enum):
    """Break of structure direction."""

    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class BOSConfig:
    """Configuration for Break-of-Structure detection."""

    require_close_break: bool = True
    confirmation_candles: int = 1
    minimum_break_points: float = 0.0
    atr_filter: bool = False


class BOSDetector:
    """Detect bullish and bearish break-of-structure events."""

    def __init__(self, config: BOSConfig | None = None) -> None:
        self.config = config or BOSConfig()

    def detect(self, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> list[StructureSignal]:
        """Detect BOS events using prior swing highs and lows."""
        if not candles:
            return []

        latest = candles[-1]
        signals: list[StructureSignal] = []
        seen: set[tuple[int, float, object, str]] = set()

        for signal in swings:
            if signal.type != StructureType.BOS:
                continue

            direction = self._normalize_direction(signal.direction)
            if direction is None:
                continue

            signature = (signal.index, signal.price, signal.timestamp, direction.value)
            if signature in seen:
                continue
            seen.add(signature)

            if self._is_bos(signal, latest, direction):
                signals.append(signal)

        return signals

    def _is_bos(self, signal: StructureSignal, candle: Candle, direction: BreakOfStructureType) -> bool:
        if signal.type != StructureType.BOS:
            return False

        reference = signal.price
        if direction == BreakOfStructureType.BULLISH:
            break_price = candle.close if self.config.require_close_break else candle.high
            broken = break_price > reference
            if not broken or break_price == reference:
                return False
            return self._is_minimum_break_distance(break_price, reference)

        if direction == BreakOfStructureType.BEARISH:
            break_price = candle.close if self.config.require_close_break else candle.low
            broken = break_price < reference
            if not broken or break_price == reference:
                return False
            return self._is_minimum_break_distance(reference, break_price)

        return False

    @staticmethod
    def _normalize_direction(direction: object) -> BreakOfStructureType | None:
        if isinstance(direction, BreakOfStructureType):
            return direction

        if direction is None:
            return None

        normalized = str(direction).lower()
        if normalized in {BreakOfStructureType.BULLISH.value, TrendState.UPTREND.value, "uptrend"}:
            return BreakOfStructureType.BULLISH
        if normalized in {BreakOfStructureType.BEARISH.value, TrendState.DOWNTREND.value, "downtrend"}:
            return BreakOfStructureType.BEARISH
        return None

    def _is_minimum_break_distance(self, value: float, reference: float) -> bool:
        return abs(value - reference) >= self.config.minimum_break_points
