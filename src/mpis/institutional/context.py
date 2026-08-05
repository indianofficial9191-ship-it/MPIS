"""Institutional context engine for MPIS (Sprint 5 Batch 5.3).

Provides a deterministic InstitutionalContextEngine that summarizes high-timeframe
bias, liquidity contexts, dealing range context, alignments and a confidence score.

This module is intentionally self-contained and does not modify existing modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class HTFBias(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


class LiquidityClassification(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class LiquidityContext:
    value: float
    classification: LiquidityClassification


@dataclass(frozen=True)
class DealingRangeContext:
    low: float
    high: float
    center: float
    width: float


@dataclass(frozen=True)
class InstitutionalContext:
    htf_bias: Dict[str, HTFBias]
    htf_score: float
    internal_liquidity: LiquidityContext
    external_liquidity: LiquidityContext
    dealing_range: DealingRangeContext
    trend_alignment: bool
    liquidity_alignment: bool
    premium_discount_alignment: str
    confidence: float


class InstitutionalContextEngine:
    """Engine to compute institutional context and a deterministic confidence score.

    analyze(...) accepts simple, explicit inputs and returns an InstitutionalContext.

    - htf_bias: mapping for keys 'daily','weekly','monthly' -> HTFBias values
    - internal_liquidity / external_liquidity: floats >= 0 (interpreted relative)
    - dealing_range: (low, high) tuple where high >= low
    - trend_alignment: whether short-term trend aligns with institutional bias
    - liquidity_alignment: whether internal and external liquidity contexts align
    - premium_discount_alignment: one of 'premium','discount','equilibrium' describing
      whether current price sits as premium/discount versus a swing (caller-provided)

    The engine is deterministic and uses simple weighted heuristics to compute
    the confidence score. All numeric outputs are clipped to 0..1 where relevant.
    """

    def analyze(
        self,
        htf_bias: Dict[str, str],
        internal_liquidity: float,
        external_liquidity: float,
        dealing_range: Tuple[float, float],
        trend_alignment: bool,
        liquidity_alignment: bool,
        premium_discount_alignment: str,
    ) -> InstitutionalContext:
        # Validate HTF bias keys and normalize
        expected_keys = ("daily", "weekly", "monthly")
        normalized: dict[str, HTFBias] = {}
        for key in expected_keys:
            raw = htf_bias.get(key)
            if raw is None:
                normalized[key] = HTFBias.NEUTRAL
            else:
                raw_norm = str(raw).lower()
                if "bull" in raw_norm:
                    normalized[key] = HTFBias.BULL
                elif "bear" in raw_norm:
                    normalized[key] = HTFBias.BEAR
                else:
                    normalized[key] = HTFBias.NEUTRAL

        # Liquidity classification (deterministic thresholds)
        def classify_liquidity(value: float) -> LiquidityContext:
            # allow values >=0; interpret relative to 1.0 scale
            v = float(value)
            if v >= 0.7:
                cls = LiquidityClassification.HIGH
            elif v >= 0.3:
                cls = LiquidityClassification.MEDIUM
            else:
                cls = LiquidityClassification.LOW
            return LiquidityContext(value=round(v, 3), classification=cls)

        internal_ctx = classify_liquidity(internal_liquidity)
        external_ctx = classify_liquidity(external_liquidity)

        # Dealing range validation
        low, high = dealing_range
        if high < low:
            raise ValueError("dealing_range high must be >= low")
        center = (low + high) / 2.0
        width = high - low
        dealing_ctx = DealingRangeContext(low=low, high=high, center=center, width=width)

        # HTF score: bulls +1, neutrals 0, bears -1, normalized to [0,1]
        score_raw = 0
        for v in normalized.values():
            if v == HTFBias.BULL:
                score_raw += 1
            elif v == HTFBias.BEAR:
                score_raw -= 1
        # score_raw in [-3..3] -> map to [0..1]
        htf_score = (score_raw + 3) / 6.0

        # Alignment scoring
        # trend_alignment and liquidity_alignment are booleans; premium_discount_alignment
        # is 'premium'|'discount'|'equilibrium' — treat 'equilibrium' as neutral.
        pd_align = str(premium_discount_alignment).lower()
        if pd_align not in ("premium", "discount", "equilibrium"):
            pd_align = "equilibrium"

        # Compute component scores
        trend_score = 1.0 if trend_alignment else 0.0
        liquidity_align_score = 1.0 if liquidity_alignment else 0.0
        # premium/discount alignment: if premium and HTF bullish -> 1.0, if discount and HTF bearish ->1.0,
        # equilibrium -> 0.5, otherwise 0.0
        pd_score = 0.5
        if pd_align == "equilibrium":
            pd_score = 0.5
        elif pd_align == "premium" and htf_score > 0.5:
            pd_score = 1.0
        elif pd_align == "discount" and htf_score < 0.5:
            pd_score = 1.0
        else:
            pd_score = 0.0

        # Confidence composition (weights chosen to prioritize HTF + alignments)
        # base 0.1, HTF weight 0.3, trend 0.25, liquidity 0.2, pd 0.15
        confidence = 0.1 + htf_score * 0.3 + trend_score * 0.25 + liquidity_align_score * 0.2 + pd_score * 0.15

        # Penalize obvious conflicts: if HTF mixed (not all same and not neutral majority) reduce
        bulls = sum(1 for v in normalized.values() if v == HTFBias.BULL)
        bears = sum(1 for v in normalized.values() if v == HTFBias.BEAR)
        if bulls > 0 and bears > 0:
            confidence -= 0.15

        # Clip
        confidence = max(0.0, min(1.0, round(confidence, 3)))

        return InstitutionalContext(
            htf_bias=normalized,
            htf_score=round(htf_score, 3),
            internal_liquidity=internal_ctx,
            external_liquidity=external_ctx,
            dealing_range=dealing_ctx,
            trend_alignment=bool(trend_alignment),
            liquidity_alignment=bool(liquidity_alignment),
            premium_discount_alignment=pd_align,
            confidence=confidence,
        )
