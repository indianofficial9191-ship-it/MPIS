"""Change-of-character detection for MPIS market structure analysis."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from mpis.data.candle import Candle
from mpis.structure.models import StructureSignal, StructureType, TrendState


class CHOCHDirection(str, Enum):
    """CHOCH direction classifications."""

    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(frozen=True)
class CHOCHConfig:
    """Configuration for CHOCH detection."""

    confirmation_candles: int = 1
    require_close_break: bool = True
    minimum_break_points: float = 0.0
    atr_filter: bool = False


class CHOCHDetector:
    """Detect changes-of-character in market structure."""

    def __init__(self, config: CHOCHConfig | None = None) -> None:
        self.config = config or CHOCHConfig()

    def detect(self, trend: TrendState, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> list[StructureSignal]:
        """Detect CHOCH based on trend direction and swing break events."""
        if not candles:
            return []

        if trend == TrendState.UPTREND:
            return self._detect_bearish_choch(swings, candles)
        if trend == TrendState.DOWNTREND:
            return self._detect_bullish_choch(swings, candles)
        return []

    def _detect_bearish_choch(self, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> list[StructureSignal]:
        return [signal for signal in swings if self._is_bearish_choch(signal, swings, candles)]

    def _detect_bullish_choch(self, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> list[StructureSignal]:
        return [signal for signal in swings if self._is_bullish_choch(signal, swings, candles)]

    def _is_bullish_choch(self, signal: StructureSignal, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> bool:
        if signal.type != StructureType.CHOCH or self._normalize_direction(signal.direction) != CHOCHDirection.BULLISH:
            return False

        latest = candles[-1]
        reference_signal = self._previous_reference_signal(swings, signal)
        if reference_signal is None:
            return False

        reference_price = reference_signal.price
        break_price = latest.close if self.config.require_close_break else latest.high
        broken = break_price > reference_price
        if not broken or break_price == reference_price:
            return False
        return self._is_minimum_break_distance(break_price, reference_price)

    def _is_bearish_choch(self, signal: StructureSignal, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> bool:
        if signal.type != StructureType.CHOCH or self._normalize_direction(signal.direction) != CHOCHDirection.BEARISH:
            return False

        latest = candles[-1]
        reference_signal = self._previous_reference_signal(swings, signal)
        if reference_signal is None:
            return False

        reference_price = reference_signal.price
        break_price = latest.close if self.config.require_close_break else latest.low
        broken = break_price < reference_price
        if not broken or break_price == reference_price:
            return False
        return self._is_minimum_break_distance(reference_price, break_price)

    @staticmethod
    def _normalize_direction(direction: object) -> CHOCHDirection | None:
        if isinstance(direction, CHOCHDirection):
            return direction
        if direction is None:
            return None
        normalized = str(direction).lower()
        if normalized in {CHOCHDirection.BULLISH.value, "uptrend"}:
            return CHOCHDirection.BULLISH
        if normalized in {CHOCHDirection.BEARISH.value, "downtrend"}:
            return CHOCHDirection.BEARISH
        return None

    @staticmethod
    def _previous_reference_signal(swings: Sequence[StructureSignal], signal: StructureSignal) -> StructureSignal | None:
        for candidate in reversed(tuple(swings)):
            if candidate is signal:
                continue
            return candidate
        return None

    def _is_minimum_break_distance(self, value: float, reference: float) -> bool:
        return abs(value - reference) >= self.config.minimum_break_points
