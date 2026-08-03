"""Unified liquidity engine for Sprint 3 detectors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.data.candle import Candle
from mpis.liquidity.equal_high_low import EqualHighDetector, EqualLowDetector
from mpis.liquidity.grab import GrabDetector
from mpis.liquidity.liquidity_pool import LiquidityPoolConfig, LiquidityPoolDetector
from mpis.liquidity.models import LiquidityEngineResult
from mpis.liquidity.stop_hunt import StopHuntConfig, StopHuntDetector


@dataclass(frozen=True)
class LiquidityEngineConfig:
    """Configuration for the liquidity engine."""

    equal_high_tolerance: float = 0.3
    equal_low_tolerance: float = 0.3
    liquidity_pool_lookback: int = 3
    stop_hunt_threshold: float = 1.0


class LiquidityEngine:
    """Orchestrate the Sprint 3 liquidity detectors into one API."""

    def __init__(self, config: LiquidityEngineConfig | None = None) -> None:
        self.config = config or LiquidityEngineConfig()
        self.equal_high_detector = EqualHighDetector(tolerance=self.config.equal_high_tolerance)
        self.equal_low_detector = EqualLowDetector(tolerance=self.config.equal_low_tolerance)
        self.liquidity_pool_detector = LiquidityPoolDetector(
            config=LiquidityPoolConfig(
                lookback=self.config.liquidity_pool_lookback,
                minimum_touches=2,
                price_tolerance=0.3,
                confidence_threshold=0.75,
            )
        )
        self.stop_hunt_detector = StopHuntDetector(
            config=StopHuntConfig(
                sweep_threshold=self.config.stop_hunt_threshold,
                rejection_threshold=0.5,
                require_close_back=True,
            )
        )
        self.grab_detector = GrabDetector()

    def analyze(self, candles: Sequence[Candle]) -> LiquidityEngineResult:
        """Run all detectors and aggregate their results."""
        equal_highs = self.equal_high_detector.detect(candles)
        equal_lows = self.equal_low_detector.detect(candles)
        liquidity_pools = self.liquidity_pool_detector.detect(candles)
        stop_hunts = self.stop_hunt_detector.detect(candles)
        grabs = self.grab_detector.detect(candles)

        return LiquidityEngineResult(
            equal_highs=tuple(equal_highs),
            equal_lows=tuple(equal_lows),
            pools=tuple(liquidity_pools),
            stop_hunts=tuple(stop_hunts),
            liquidity_grabs=tuple(grabs),
        )
