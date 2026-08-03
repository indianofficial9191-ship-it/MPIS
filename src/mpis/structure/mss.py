"""Market structure shift detection for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.structure.models import StructureSignal, StructureType, TrendState
from mpis.structure.bos import BOSConfig, BOSDetector
from mpis.structure.choch import CHOCHConfig, CHOCHDetector


@dataclass(frozen=True)
class MSSConfig:
    """Configuration for market structure shift detection."""

    require_close_break: bool = True
    confirmation_candles: int = 1
    minimum_break_points: float = 0.0
    atr_filter: bool = False
    use_liquidity_confirmation: bool = True
    use_swing_confirmation: bool = True


@dataclass(frozen=True)
class MSSAnalysis:
    """Result of MSS detection."""

    trend: TrendState
    choch: StructureSignal | None
    bos: StructureSignal | None
    confidence: float


class MSSDetector:
    """Detect market structure shifts from structure and liquidity events."""

    def __init__(self, config: MSSConfig | None = None) -> None:
        self.config = config or MSSConfig()
        self.bos_detector = BOSDetector(BOSConfig(
            require_close_break=self.config.require_close_break,
            confirmation_candles=self.config.confirmation_candles,
            minimum_break_points=self.config.minimum_break_points,
            atr_filter=self.config.atr_filter,
        ))
        self.choch_detector = CHOCHDetector(CHOCHConfig(
            require_close_break=self.config.require_close_break,
            confirmation_candles=self.config.confirmation_candles,
            minimum_break_points=self.config.minimum_break_points,
            atr_filter=self.config.atr_filter,
        ))

    def detect(
        self,
        trend: TrendState,
        swings: Sequence[StructureSignal],
        candles: Sequence[StructureSignal | Candle],
    ) -> MSSAnalysis | None:
        """Detect a market structure shift when BOS and CHOCH signals align."""
        candle_objects = self._extract_candles(candles)
        choch_signals = self.choch_detector.detect(trend, swings, candle_objects)
        bos_signals = self.bos_detector.detect(swings, candle_objects)

        latest_choch = choch_signals[-1] if choch_signals else None
        latest_bos = bos_signals[-1] if bos_signals else None

        if latest_choch is None and latest_bos is None:
            fallback_choch = self._latest_signal(swings, StructureType.CHOCH)
            fallback_bos = self._latest_signal(swings, StructureType.BOS)
            if fallback_choch is None and fallback_bos is None:
                return None
            latest_choch = latest_choch or fallback_choch
            latest_bos = latest_bos or fallback_bos

        if latest_choch is None and latest_bos is None:
            return None

        if latest_choch is not None and latest_bos is not None:
            confidence = 1.0
        elif latest_bos is not None or latest_choch is not None:
            confidence = 1.0
        else:
            confidence = 0.0

        return MSSAnalysis(trend=trend, choch=latest_choch, bos=latest_bos, confidence=confidence)

    @staticmethod
    def _latest_signal(swings: Sequence[StructureSignal], signal_type: StructureType) -> StructureSignal | None:
        for signal in reversed(tuple(swings)):
            if signal.type == signal_type:
                return signal
        return None

    @staticmethod
    def _extract_candles(candles: Sequence[StructureSignal | Candle]) -> list[Candle]:
        candle_objects: list[Candle] = []
        for item in candles:
            if isinstance(item, Candle):
                candle_objects.append(item)
            elif isinstance(item, StructureSignal) and item.candle is not None:
                candle_objects.append(item.candle)
        return candle_objects
