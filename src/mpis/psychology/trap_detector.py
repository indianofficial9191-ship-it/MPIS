"""Trap detection for MPIS psychology sprint 5B."""
from __future__ import annotations

from typing import Sequence

from mpis.data.candle import Candle
from mpis.psychology.fake_breakout import FakeBreakoutDetector
from mpis.psychology.liquidity_grab import LiquidityGrabDetector
from mpis.psychology.models import (
    FakeBreakoutConfig,
    LiquidityGrabResult,
    TrapConfig,
    TrapResult,
    TrapType,
    WickAnalysisClassification,
)
from mpis.psychology.stop_hunt import StopHuntDetector
from mpis.psychology.wick_analysis import WickAnalyzer


class TrapDetector:
    """Detect bull and bear traps using structure, liquidity, and rejection signals."""

    def __init__(self, config: TrapConfig | None = None) -> None:
        self.config = config or TrapConfig()

    def detect(self, candles: Sequence[Candle]) -> TrapResult:
        """Return a trap detection result for the provided candle sequence."""
        if len(candles) < self.config.confirmation_candles + 2:
            return TrapResult(
                trap_type=TrapType.NONE,
                confidence=0.0,
                liquidity_detected=False,
                structure_detected=False,
                rejection_detected=False,
                explanation="Insufficient candles to detect a trap.",
            )

        sorted_candles = sorted(candles, key=lambda candle: candle.timestamp)
        last_candle = sorted_candles[-1]

        structure_signals = FakeBreakoutDetector(
            config=FakeBreakoutConfig(confirmation_candles=self.config.confirmation_candles)
        ).detect(sorted_candles)
        wick_result = WickAnalyzer().analyze(last_candle)
        liquidity_signals = LiquidityGrabDetector().detect(sorted_candles)
        stop_hunt_signals = StopHuntDetector().detect(sorted_candles)

        structure_detected = bool(structure_signals)
        liquidity_detected = any(signal.found for signal in liquidity_signals) or any(signal.found for signal in stop_hunt_signals)
        rejection_detected = wick_result.classification != WickAnalysisClassification.NEUTRAL

        bull_trap = (
            structure_detected
            and rejection_detected
            and liquidity_detected
            and any(signal.direction == "up" for signal in structure_signals)
            and wick_result.classification == WickAnalysisClassification.BEARISH_REJECTION
        )
        bear_trap = (
            structure_detected
            and rejection_detected
            and liquidity_detected
            and any(signal.direction == "down" for signal in structure_signals)
            and wick_result.classification == WickAnalysisClassification.BULLISH_REJECTION
        )

        if bull_trap:
            trap_type = TrapType.BULL_TRAP
            explanation = "Detected a bull trap: false upside structure failure with liquidity and bearish rejection."
        elif bear_trap:
            trap_type = TrapType.BEAR_TRAP
            explanation = "Detected a bear trap: false downside structure failure with liquidity and bullish rejection."
        else:
            return TrapResult(
                trap_type=TrapType.NONE,
                confidence=0.0,
                liquidity_detected=liquidity_detected,
                structure_detected=structure_detected,
                rejection_detected=rejection_detected,
                explanation="No trap pattern detected.",
            )

        liquidity_confidence = max((signal.confidence for signal in liquidity_signals if signal.found), default=0.0)
        structure_confidence = max((signal.confidence for signal in structure_signals), default=0.0)
        rejection_confidence = 1.0 if rejection_detected else 0.0

        confidence = min(
            1.0,
            0.2 + structure_confidence * 0.4 + liquidity_confidence * 0.3 + rejection_confidence * 0.1,
        )

        return TrapResult(
            trap_type=trap_type,
            confidence=round(confidence, 3),
            liquidity_detected=liquidity_detected,
            structure_detected=structure_detected,
            rejection_detected=rejection_detected,
            explanation=explanation,
        )
