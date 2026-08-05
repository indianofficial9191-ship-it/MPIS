"""MPIS pipeline orchestration (Sprint 6 Batch 6.1).

MpisPipeline composes analysis engines in a deterministic order and returns a
PipelineResult containing outputs from each stage. Engines are injected to keep
the pipeline testable and decoupled from implementations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineResult:
    market_structure: Any
    liquidity: Any
    smc: Any
    trend: Any
    premium_discount: Any
    psychology: Any
    fusion: Any
    probability: Any


class MpisPipeline:
    """Orchestrate analysis engines in a fixed, deterministic order.

    Order:
      1. Market Structure
      2. Liquidity
      3. Smart Money (SMC)
      4. Trend Context
      5. Premium Discount
      6. Psychology Score
      7. Trade Fusion
      8. Probability Engine

    Engines are provided via constructor injection to make the pipeline
    deterministic and unit-test friendly.
    """

    def __init__(
        self,
        market_structure_engine: object,
        liquidity_engine: object,
        smc_engine: object,
        trend_engine: object,
        premium_engine: object,
        psychology_engine: object,
        fusion_engine: object,
        probability_engine: object,
    ) -> None:
        self.market_structure_engine = market_structure_engine
        self.liquidity_engine = liquidity_engine
        self.smc_engine = smc_engine
        self.trend_engine = trend_engine
        self.premium_engine = premium_engine
        self.psychology_engine = psychology_engine
        self.fusion_engine = fusion_engine
        self.probability_engine = probability_engine

    def run(self, dataframe: object | None = None, candles: object | None = None, current_price: float | None = None) -> PipelineResult:
        """Execute the pipeline stages and return a PipelineResult.

        Parameters:
            dataframe: pandas.DataFrame or any object required by market structure engine
            candles: sequence of Candle objects or any object required by liquidity/smc/psychology engines
            current_price: optional float price used by premium discount engine; if None, attempts to derive from candles
        """
        # 1. Market Structure
        market_structure = None
        if hasattr(self.market_structure_engine, "analyze"):
            # MarketStructureAnalyzer.analyze expects a dataframe
            market_structure = self.market_structure_engine.analyze(dataframe)

        # 2. Liquidity
        liquidity = None
        if hasattr(self.liquidity_engine, "analyze"):
            liquidity = self.liquidity_engine.analyze(candles)

        # 3. Smart Money (SMC)
        smc = None
        if hasattr(self.smc_engine, "analyze"):
            smc = self.smc_engine.analyze(candles)

        # 4. Trend Context
        trend = None
        if hasattr(self.trend_engine, "analyze"):
            # trend engine accepts swings as the 'swings' parameter
            trend = self.trend_engine.analyze(None, (), (), None, market_structure)

        # 5. Premium Discount
        premium = None
        if hasattr(self.premium_engine, "analyze"):
            # Determine swing_high and swing_low if market_structure provides swings
            sh = None
            sl = None
            if market_structure and isinstance(market_structure, (list, tuple)) and market_structure:
                # try to extract numeric prices if swing objects exist
                first = market_structure[0]
                sh = getattr(first, "end_price", None) or getattr(first, "price", None) or getattr(first, "end_price", None)
                sl = getattr(first, "start_price", None) or getattr(first, "price", None) or getattr(first, "start_price", None)
            # fall back to current_price if provided
            if sh is None or sl is None:
                if current_price is not None:
                    sh = sh or float(current_price)
                    sl = sl or float(current_price)
                else:
                    # final fallback: use zeros to avoid exceptions
                    sh = sh or 0.0
                    sl = sl or 0.0
            premium = self.premium_engine.analyze(float(current_price) if current_price is not None else float(sh), float(sh), float(sl))

        # 6. Psychology Score
        psychology = None
        if hasattr(self.psychology_engine, "analyze"):
            psychology = self.psychology_engine.analyze(trend, premium, liquidity, smc)

        # 7. Trade Fusion
        fusion = None
        if hasattr(self.fusion_engine, "analyze"):
            fusion = self.fusion_engine.analyze(psychology, trend, premium, liquidity, smc)

        # 8. Probability
        probability = None
        if hasattr(self.probability_engine, "analyze") and fusion is not None:
            probability = self.probability_engine.analyze(fusion)

        return PipelineResult(
            market_structure=market_structure,
            liquidity=liquidity,
            smc=smc,
            trend=trend,
            premium_discount=premium,
            psychology=psychology,
            fusion=fusion,
            probability=probability,
        )
