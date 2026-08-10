"""Sprint 9 unified MPIS signal engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import SignalInput, SignalSide, UnifiedSignal


@dataclass(frozen=True)
class UnifiedSignalEngine:
    minimum_confidence: float = 0.65
    minimum_alignment: float = 0.60
    maximum_risk: float = 0.60

    def generate(
        self,
        inputs: tuple[SignalInput, ...] | list[SignalInput],
    ) -> UnifiedSignal:
        items = tuple(inputs)

        if not items:
            return UnifiedSignal(
                side=SignalSide.HOLD,
                confidence=0.0,
                quality="NONE",
                direction_bias="NEUTRAL",
                trap_warning=False,
                risk_score=0.0,
                alignment_score=0.0,
            )

        buy = 0.0
        sell = 0.0
        total = 0.0
        risk = 0.0
        trap = False
        reasons: list[str] = []
        risk_flags: list[str] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))
            weight = max(0.0, float(item.weight))

            if weight == 0:
                continue

            contribution = confidence * weight
            total += weight

            side = item.side.upper()

            if side == "BUY":
                buy += contribution
                reasons.append(f"{item.name}: BUY")
            elif side == "SELL":
                sell += contribution
                reasons.append(f"{item.name}: SELL")

            if item.risk_flag:
                risk += weight
                risk_flags.append(item.name)

            if item.trap_flag:
                trap = True

        if total == 0:
            return UnifiedSignal(
                side=SignalSide.HOLD,
                confidence=0.0,
                quality="NONE",
                direction_bias="NEUTRAL",
                trap_warning=trap,
                risk_score=0.0,
                alignment_score=0.0,
                reasons=tuple(reasons),
                risk_flags=tuple(risk_flags),
            )

        buy_ratio = buy / total
        sell_ratio = sell / total

        dominant = max(buy_ratio, sell_ratio)
        opposing = min(buy_ratio, sell_ratio)

        alignment = max(0.0, min(1.0, dominant - opposing * 0.40))
        risk_score = min(1.0, risk / total)

        confidence = max(
            0.0,
            min(1.0, alignment - risk_score * 0.25),
        )

        if buy_ratio > sell_ratio:
            bias = "BULLISH"
        elif sell_ratio > buy_ratio:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        if (
            buy_ratio > sell_ratio
            and confidence >= self.minimum_confidence
            and alignment >= self.minimum_alignment
            and risk_score <= self.maximum_risk
            and not trap
        ):
            side = SignalSide.BUY
        elif (
            sell_ratio > buy_ratio
            and confidence >= self.minimum_confidence
            and alignment >= self.minimum_alignment
            and risk_score <= self.maximum_risk
            and not trap
        ):
            side = SignalSide.SELL
        else:
            side = SignalSide.HOLD

        if side == SignalSide.HOLD:
            quality = "WEAK"
        elif confidence >= 0.80:
            quality = "STRONG"
        else:
            quality = "VALID"

        return UnifiedSignal(
            side=side,
            confidence=confidence,
            quality=quality,
            direction_bias=bias,
            trap_warning=trap,
            risk_score=risk_score,
            alignment_score=alignment,
            reasons=tuple(reasons),
            risk_flags=tuple(risk_flags),
        )