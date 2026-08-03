"""High-level market structure detector for MPIS."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from mpis.data.candle import Candle
from mpis.structure.bos import BOSConfig, BOSDetector
from mpis.structure.choch import CHOCHConfig, CHOCHDetector
from mpis.structure.mss import MSSConfig, MSSDetector
from mpis.structure.models import StructureSignal, TrendState
from mpis.structure.trend import TrendDetector


@dataclass(frozen=True)
class StructureDetectorConfig:
    """Runtime configuration for structure detection."""

    confirmation_candles: int = 1
    require_close_break: bool = True
    minimum_break_points: float = 5.0
    atr_filter: bool = False
    use_liquidity_confirmation: bool = True
    use_swing_confirmation: bool = True


@dataclass(frozen=True)
class StructureOutput:
    """Output of the market structure detector."""

    trend: TrendState
    latest_bos: StructureSignal | None
    latest_choch: StructureSignal | None
    strength: float
    confidence: float


class StructureDetector:
    """Combine trend, BOS, CHOCH, and MSS detection into a single engine."""

    def __init__(self, config: StructureDetectorConfig | None = None) -> None:
        self.config = config or StructureDetectorConfig()
        self.trend_detector = TrendDetector()
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
        self.mss_detector = MSSDetector(MSSConfig(
            require_close_break=self.config.require_close_break,
            confirmation_candles=self.config.confirmation_candles,
            minimum_break_points=self.config.minimum_break_points,
            atr_filter=self.config.atr_filter,
            use_liquidity_confirmation=self.config.use_liquidity_confirmation,
            use_swing_confirmation=self.config.use_swing_confirmation,
        ))

    def analyze(self, swings: Sequence[StructureSignal], candles: Sequence[Candle]) -> StructureOutput:
        """Analyze market structure using swings and recent candles."""
        trend_analysis = self.trend_detector.detect(swings)
        latest_bos = self._last_signal(self.bos_detector.detect(swings, candles))
        latest_choch = self._last_signal(self.choch_detector.detect(trend_analysis.trend, swings, candles))
        mss_signals = [signal for signal in [latest_bos, latest_choch] if signal is not None]
        mss = self.mss_detector.detect(trend_analysis.trend, swings, mss_signals)

        confidence = mss.confidence if mss else 0.0
        strength = 1.0 if trend_analysis.trend != TrendState.RANGE else 0.5

        return StructureOutput(
            trend=trend_analysis.trend,
            latest_bos=latest_bos,
            latest_choch=latest_choch,
            strength=strength,
            confidence=confidence,
        )

    @staticmethod
    def _last_signal(signals: Sequence[StructureSignal]) -> StructureSignal | None:
        return signals[-1] if signals else None
