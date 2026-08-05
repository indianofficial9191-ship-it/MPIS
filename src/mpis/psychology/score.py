"""Psychology scoring engine for MPIS (Sprint 5 Batch 5.4).

Produces a deterministic bullish/bearish score, confidence and bias with
explanatory reasons from trend, premium/discount, liquidity and SMC inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from mpis.psychology.models import TrendContext
from mpis.psychology.premium_discount import PremiumDiscountAnalysis
from mpis.psychology.models import LiquidityGrabResult
from mpis.smc.models import SMCEngineResult


class MarketBias(str, Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass(frozen=True)
class PsychologyScore:
    bullish_score: float
    bearish_score: float
    confidence: float  # 0..100
    bias: MarketBias
    reasons: List[str]


class PsychologyScoreEngine:
    """Engine to compute psychology scores from multiple analyses.

    The engine is deterministic and uses fixed weights. All numeric outputs are
    rounded to two decimals for clarity.
    """

    def analyze(
        self,
        trend_context: TrendContext,
        premium_analysis: PremiumDiscountAnalysis,
        liquidity_analysis: LiquidityGrabResult | List[LiquidityGrabResult] | None,
        smc_analysis: SMCEngineResult | None,
    ) -> PsychologyScore:
        reasons: List[str] = []

        # Base scores from trend strength
        trend_map = {
            "very_bullish": (40.0, 0.0),
            "bullish": (30.0, 0.0),
            "weak_bullish": (15.0, 0.0),
            "sideways": (0.0, 0.0),
            "weak_bearish": (0.0, 15.0),
            "bearish": (0.0, 30.0),
            "very_bearish": (0.0, 40.0),
        }

        trend_key = getattr(trend_context.trend, "value", str(trend_context.trend)).lower()
        bullish_score, bearish_score = trend_map.get(trend_key, (0.0, 0.0))
        reasons.append(f"Trend {trend_context.trend.value} contributes +{int(bullish_score)} bullish / +{int(bearish_score)} bearish")

        # Premium/Discount influence
        pd_zone = getattr(premium_analysis, "zone", None)
        if pd_zone is not None:
            pd_zone_str = str(pd_zone).lower()
            if "discount" in pd_zone_str:
                bullish_score += 20.0
                reasons.append("Discount zone adds +20 bullish")
            elif "premium" in pd_zone_str:
                bearish_score += 20.0
                reasons.append("Premium zone adds +20 bearish")
            else:
                reasons.append("Equilibrium zone adds no directional weight")

        # Liquidity analysis influence
        liquidity_confirmed = False
        liquidity_bullish = False
        liquidity_bearish = False

        if liquidity_analysis is None:
            reasons.append("No liquidity analysis provided")
        else:
            # normalize to list
            items = liquidity_analysis if isinstance(liquidity_analysis, list) else [liquidity_analysis]
            for item in items:
                found = getattr(item, "found", False)
                if not found:
                    continue
                liquidity_confirmed = True
                direction = getattr(item, "direction", None)
                if direction is not None and "bull" in str(direction).lower():
                    liquidity_bullish = True
                if direction is not None and "bear" in str(direction).lower():
                    liquidity_bearish = True

            if liquidity_confirmed:
                # increase confidence and favor direction
                reasons.append("Liquidity grab detected; increases confidence")
                if liquidity_bullish and not liquidity_bearish:
                    bullish_score += 10.0
                    reasons.append("Liquidity grab bullish adds +10 bullish")
                if liquidity_bearish and not liquidity_bullish:
                    bearish_score += 10.0
                    reasons.append("Liquidity grab bearish adds +10 bearish")

        # SMC analysis influence
        smc_confirmed = False
        if smc_analysis is None:
            reasons.append("No SMC analysis provided")
        else:
            # if any of the result tuples are non-empty we consider SMC confirmation
            has_fvg = bool(getattr(smc_analysis, "fvgs", ()))
            has_imbalances = bool(getattr(smc_analysis, "imbalances", ()))
            has_order_blocks = bool(getattr(smc_analysis, "order_blocks", ()))
            if has_fvg or has_imbalances or has_order_blocks:
                smc_confirmed = True
                reasons.append("SMC signals present; increases confidence")

        # Begin confidence composition (base from trend_context.confidence 0..1 scaled to 0..100)
        confidence = float(trend_context.confidence) * 100.0
        reasons.append(f"Base confidence from trend context: {round(confidence,2)}")

        if liquidity_confirmed:
            confidence += 10.0
            reasons.append("+10 for liquidity confirmation")
        if smc_confirmed:
            confidence += 10.0
            reasons.append("+10 for SMC confirmation")

        # Alignment: if trend_context indicates MSS/BOS and SMC or liquidity agree increase
        alignment_bonus = 0.0
        if trend_context.mss_confirmed and liquidity_confirmed:
            alignment_bonus += 5.0
            reasons.append("+5 alignment bonus for MSS and liquidity agreement")
        if trend_context.bos_confirmed and smc_confirmed:
            alignment_bonus += 5.0
            reasons.append("+5 alignment bonus for BOS and SMC agreement")
        confidence += alignment_bonus

        # Conflicts reduce confidence
        # Conflict examples: trend bullish but premium is premium (favoring bearish), or liquidity and trend disagree
        conflict_penalty = 0.0
        # trend bullish vs premium premium
        if bullish_score > bearish_score and pd_zone is not None and "premium" in str(pd_zone).lower():
            conflict_penalty += 15.0
            reasons.append("Conflict: bullish trend vs premium zone -> -15 confidence")
        if bearish_score > bullish_score and pd_zone is not None and "discount" in str(pd_zone).lower():
            conflict_penalty += 15.0
            reasons.append("Conflict: bearish trend vs discount zone -> -15 confidence")
        # liquidity vs trend
        if liquidity_confirmed and ((liquidity_bullish and bearish_score > bullish_score) or (liquidity_bearish and bullish_score > bearish_score)):
            conflict_penalty += 10.0
            reasons.append("Conflict between liquidity direction and trend/bias -> -10 confidence")

        confidence -= conflict_penalty

        # Final bias selection
        # Normalize scores and decide bias
        bullish_score = round(float(bullish_score), 2)
        bearish_score = round(float(bearish_score), 2)

        # Determine bias thresholds
        diff = bullish_score - bearish_score
        if diff >= 30:
            bias = MarketBias.STRONG_BUY
        elif diff >= 10:
            bias = MarketBias.BUY
        elif diff <= -30:
            bias = MarketBias.STRONG_SELL
        elif diff <= -10:
            bias = MarketBias.SELL
        else:
            bias = MarketBias.NEUTRAL

        # Clamp confidence 0..100
        confidence = max(0.0, min(100.0, round(confidence, 2)))

        return PsychologyScore(
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            confidence=confidence,
            bias=bias,
            reasons=reasons,
        )
