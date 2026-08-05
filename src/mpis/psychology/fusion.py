"""Trade fusion engine for MPIS (Sprint 5 Batch 5.5).

Combines psychology score, trend, premium/discount, liquidity and SMC analyses
into a single trade decision using a deterministic weighted fusion approach.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from mpis.psychology.score import PsychologyScore
from mpis.psychology.models import TrendContext, TrendStrength, LiquidityGrabResult
from mpis.psychology.premium_discount import PremiumDiscountAnalysis, ZoneType
from mpis.smc.models import SMCEngineResult


class TradeDecision(str, Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass(frozen=True)
class TradeFusionResult:
    decision: TradeDecision
    confidence: float  # 0..100
    risk_score: float  # 0..100 (higher = more risk)
    reward_score: float  # 0..100 (higher = more reward)
    reasons: List[str]


class TradeFusionEngine:
    """Deterministic fusion engine.

    Weights (sum == 1.0):
      - psychology score confidence: 0.35
      - trend context confidence: 0.30
      - premium/discount zone: 0.15
      - liquidity analysis: 0.10
      - smc analysis presence/direction: 0.10
    """

    WEIGHTS = {
        "psych": 0.35,
        "trend": 0.30,
        "pd": 0.15,
        "liq": 0.10,
        "smc": 0.10,
    }

    def analyze(
        self,
        psychology_score: PsychologyScore,
        trend_context: TrendContext,
        premium_analysis: PremiumDiscountAnalysis,
        liquidity_analysis: LiquidityGrabResult | List[LiquidityGrabResult] | None,
        smc_analysis: SMCEngineResult | None,
    ) -> TradeFusionResult:
        reasons: List[str] = []

        # Helper: map enums to directional values in [-1, 1]
        psy_map = {
            "strong_buy": 1.0,
            "buy": 0.6,
            "neutral": 0.0,
            "sell": -0.6,
            "strong_sell": -1.0,
        }

        trend_map = {
            TrendStrength.VERY_BULLISH: 1.0,
            TrendStrength.BULLISH: 0.7,
            TrendStrength.WEAK_BULLISH: 0.3,
            TrendStrength.SIDEWAYS: 0.0,
            TrendStrength.WEAK_BEARISH: -0.3,
            TrendStrength.BEARISH: -0.7,
            TrendStrength.VERY_BEARISH: -1.0,
        }

        pd_map = {ZoneType.PREMIUM: -0.5, ZoneType.DISCOUNT: 0.5, ZoneType.EQUILIBRIUM: 0.0}

        # Psychology component: use bias mapping scaled by psychology confidence (0..1)
        psy_bias = getattr(psychology_score.bias, "value", str(psychology_score.bias)).lower()
        psy_dir = psy_map.get(psy_bias, 0.0)
        psy_conf_scale = float(psychology_score.confidence) / 100.0
        psy_component = psy_dir * psy_conf_scale
        reasons.append(f"Psychology bias {psychology_score.bias.value} => dir {psy_dir} scaled by confidence {psy_conf_scale}")

        # Trend component: trend strength mapped and scaled by trend_context.confidence (assumed 0..1)
        trend_dir = trend_map.get(trend_context.trend, 0.0)
        trend_conf_scale = float(trend_context.confidence)
        trend_component = trend_dir * trend_conf_scale
        reasons.append(f"Trend {trend_context.trend.value} => dir {trend_dir} scaled by confidence {trend_conf_scale}")

        # Premium/Discount component
        pd_zone = getattr(premium_analysis, "zone", None)
        pd_dir = pd_map.get(pd_zone, 0.0) if pd_zone is not None else 0.0
        reasons.append(f"Premium/Discount zone {pd_zone} => dir {pd_dir}")

        # Liquidity component: aggregate list or single
        liq_dir = 0.0
        liq_conf_scale = 0.0
        if liquidity_analysis is None:
            reasons.append("No liquidity analysis")
        else:
            items = liquidity_analysis if isinstance(liquidity_analysis, list) else [liquidity_analysis]
            # compute weighted average direction using each item's confidence
            total_w = 0.0
            total_dir = 0.0
            for it in items:
                found = getattr(it, "found", False)
                if not found:
                    continue
                d = getattr(it, "direction", None)
                c = float(getattr(it, "confidence", 0.0))
                if d is None:
                    continue
                dv = 0.0
                dd = str(d).lower()
                if "bull" in dd:
                    dv = 0.6
                elif "bear" in dd:
                    dv = -0.6
                total_dir += dv * c
                total_w += c
            if total_w > 0:
                liq_dir = total_dir / total_w
                liq_conf_scale = min(1.0, total_w / len(items)) if len(items) > 0 else 0.0
                reasons.append(f"Liquidity aggregate dir {liq_dir} with avg confidence {liq_conf_scale}")
            else:
                reasons.append("Liquidity analysis present but no confirmed items")

        liq_component = liq_dir * liq_conf_scale

        # SMC component: inspect imbalances/fvgs/order_blocks for direction
        smc_dir = 0.0
        if smc_analysis is None:
            reasons.append("No SMC analysis")
        else:
            # prefer imbalances then fvgs then order_blocks for directional hint
            def first_dir(seq):
                for x in seq:
                    s = getattr(x, "direction", None)
                    if s is None:
                        continue
                    sval = str(s).lower()
                    if "bull" in sval:
                        return 0.6
                    if "bear" in sval:
                        return -0.6
                return 0.0

            smc_dir = first_dir(getattr(smc_analysis, "imbalances", ()))
            if smc_dir == 0.0:
                smc_dir = first_dir(getattr(smc_analysis, "fvgs", ()))
            if smc_dir == 0.0:
                smc_dir = first_dir(getattr(smc_analysis, "order_blocks", ()))

            if smc_dir != 0.0:
                reasons.append(f"SMC directional hint {smc_dir}")
            else:
                reasons.append("SMC present but no clear direction")

        smc_conf_scale = 0.0 if smc_analysis is None else 0.5 if (getattr(smc_analysis, "fvgs", ()) or getattr(smc_analysis, "imbalances", ()) or getattr(smc_analysis, "order_blocks", ())) else 0.0
        smc_component = smc_dir * smc_conf_scale

        # Weighted aggregation
        weights = self.WEIGHTS
        weighted = (
            psy_component * weights["psych"]
            + trend_component * weights["trend"]
            + (pd_dir * weights["pd"])
            + (liq_component * weights["liq"])
            + (smc_component * weights["smc"])
        )

        reasons.append(f"Weighted directional score {weighted}")

        # Agreement / conflict detection
        components = [psy_component, trend_component, pd_dir, liq_component, smc_component]
        signs = [1 if c > 0.001 else -1 if c < -0.001 else 0 for c in components]
        non_zero_signs = [s for s in signs if s != 0]

        agreement_bonus = 0.0
        conflict_penalty = 0.0
        if non_zero_signs:
            if all(s > 0 for s in non_zero_signs) or all(s < 0 for s in non_zero_signs):
                # strong agreement
                agreement_bonus = 0.15  # adds to confidence percent (15)
                reasons.append("Strong agreement across modules -> +15 confidence bonus")
            else:
                # mixed signals
                conflict_penalty = 0.10  # -10
                reasons.append("Conflicting signals across modules -> -10 confidence penalty")

        # Base confidence derived from absolute weighted score scaled to 0..100
        base_confidence = abs(weighted) * 100.0
        # incorporate psychology & trend confidences as supporting evidence
        support = (psy_conf_scale + trend_conf_scale) / 2.0 * 20.0  # up to +20
        confidence = base_confidence + support + (agreement_bonus * 100.0) - (conflict_penalty * 100.0)
        confidence = max(0.0, min(100.0, round(confidence, 2)))

        # Decision thresholds on the signed weighted score
        decision = TradeDecision.HOLD
        if weighted >= 0.6:
            decision = TradeDecision.STRONG_BUY
        elif weighted >= 0.2:
            decision = TradeDecision.BUY
        elif weighted <= -0.6:
            decision = TradeDecision.STRONG_SELL
        elif weighted <= -0.2:
            decision = TradeDecision.SELL
        else:
            decision = TradeDecision.HOLD

        # If confidence very low, force HOLD
        if confidence < 25.0:
            reasons.append(f"Low confidence {confidence} forces HOLD")
            decision = TradeDecision.HOLD

        # Risk/Reward heuristic (deterministic): reward proportional to confidence and alignment magnitude,
        # risk is inverse of confidence moderated by disagreement
        reward_score = round(confidence * (0.6 + abs(weighted) * 0.4), 2)
        risk_score = round(max(0.0, 100.0 - confidence) * (1.0 - abs(weighted)), 2)

        reasons.append(f"Final weighted {round(weighted,3)}, confidence {confidence}, reward {reward_score}, risk {risk_score}")

        return TradeFusionResult(
            decision=decision,
            confidence=confidence,
            risk_score=risk_score,
            reward_score=reward_score,
            reasons=reasons,
        )
