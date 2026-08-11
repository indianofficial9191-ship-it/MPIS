"""Sprint 11 live signal validation engine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import LiveSignalInput, LiveSignalResult, LiveSignalSide


@dataclass(frozen=True)
class LiveSignalEngine:
    """Validate fused signals before they are exposed as live signals."""

    minimum_confidence: float = 0.70
    minimum_alignment: float = 0.65
    maximum_risk: float = 0.60

    def validate(
        self,
        inputs: tuple[LiveSignalInput, ...] | list[LiveSignalInput],
    ) -> LiveSignalResult:
        items = tuple(inputs)

        if not items:
            return LiveSignalResult(
                side=LiveSignalSide.HOLD,
                confidence=0.0,
                direction_bias="NEUTRAL",
                quality="NONE",
                stale_warning=False,
                risk_score=0.0,
                alignment_score=0.0,
            )

        buy = 0.0
        sell = 0.0
        total = 0.0
        risk = 0.0
        stale_warning = False

        contributors: list[str] = []
        risk_flags: list[str] = []

        for item in items:
            confidence = max(0.0, min(1.0, float(item.confidence)))
            weight = max(0.0, float(item.weight))

            if weight == 0.0:
                continue

            total += weight

            if item.stale:
                stale_warning = True
                continue

            contribution = confidence * weight
            side = item.side.upper()

            if side == "BUY":
                buy += contribution
                contributors.append(item.name)
            elif side == "SELL":
                sell += contribution
                contributors.append(item.name)

            if item.risk_flag:
                risk += weight
                risk_flags.append(item.name)

        if total == 0.0:
            return LiveSignalResult(
                side=LiveSignalSide.HOLD,
                confidence=0.0,
                direction_bias="NEUTRAL",
                quality="NONE",
                stale_warning=stale_warning,
                risk_score=0.0,
                alignment_score=0.0,
            )

        buy_ratio = buy / total
        sell_ratio = sell / total

        dominant = max(buy_ratio, sell_ratio)
        opposing = min(buy_ratio, sell_ratio)

        alignment = max(
            0.0,
            min(1.0, dominant - opposing * 0.40),
        )

        risk_score = min(1.0, risk / total)

        confidence = max(
            0.0,
            min(
                1.0,
                alignment - risk_score * 0.25,
            ),
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
            and not stale_warning
        ):
            side = LiveSignalSide.BUY
        elif (
            sell_ratio > buy_ratio
            and confidence >= self.minimum_confidence
            and alignment >= self.minimum_alignment
            and risk_score <= self.maximum_risk
            and not stale_warning
        ):
            side = LiveSignalSide.SELL
        else:
            side = LiveSignalSide.HOLD

        if side == LiveSignalSide.HOLD:
            quality = "WEAK"
        elif confidence >= 0.80:
            quality = "STRONG"
        else:
            quality = "VALID"

        return LiveSignalResult(
            side=side,
            confidence=confidence,
            direction_bias=bias,
            quality=quality,
            stale_warning=stale_warning,
            risk_score=risk_score,
            alignment_score=alignment,
            contributors=tuple(contributors),
            risk_flags=tuple(risk_flags),
        )