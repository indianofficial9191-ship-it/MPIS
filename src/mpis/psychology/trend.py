"""Trend context engine for MPIS psychology sprint 5.1."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from mpis.psychology.models import TrendContext, TrendStrength


class TrendContextEngine:
    """Analyze structure and swing signals to produce a trend context."""

    def analyze(
        self,
        trend_state: object | None = None,
        bos_signals: Sequence[object] = (),
        choch_signals: Sequence[object] = (),
        mss_analysis: object | None = None,
        swings: Sequence[object] = (),
    ) -> TrendContext:
        """Return a deterministic trend context based on inputs."""
        bos_confirmed = bool(bos_signals)
        choch_confirmed = bool(choch_signals)
        mss_confirmed = bool(mss_analysis)

        swing_highs = self._extract_swing_prices(swings, expected_type="high")
        swing_lows = self._extract_swing_prices(swings, expected_type="low")

        timestamp = self._latest_timestamp(bos_signals, choch_signals, mss_analysis, swings)

        if not bos_confirmed and not choch_confirmed and not mss_confirmed and not swing_highs and not swing_lows:
            return TrendContext(
                trend=TrendStrength.SIDEWAYS,
                confidence=0.0,
                bos_confirmed=False,
                choch_confirmed=False,
                mss_confirmed=False,
                swing_highs=[],
                swing_lows=[],
                timestamp=timestamp,
            )

        trend_direction = self._infer_direction(trend_state, bos_signals, mss_analysis)
        trend_strength = self._classify_trend_strength(
            trend_direction, bos_confirmed, mss_confirmed, choch_confirmed
        )
        confidence = self._calculate_confidence(
            bos_confirmed, choch_confirmed, mss_confirmed, trend_direction, bos_signals, mss_analysis
        )

        return TrendContext(
            trend=trend_strength,
            confidence=round(confidence, 3),
            bos_confirmed=bos_confirmed,
            choch_confirmed=choch_confirmed,
            mss_confirmed=mss_confirmed,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
            timestamp=timestamp,
        )

    def _infer_direction(
        self,
        trend_state: object | None,
        bos_signals: Sequence[object],
        mss_analysis: object | None,
    ) -> str:
        normalized = None
        if trend_state is not None:
            normalized = str(getattr(trend_state, "value", trend_state)).lower()
            if "up" in normalized:
                return "up"
            if "down" in normalized:
                return "down"

        bos_direction = self._extract_latest_direction(bos_signals)
        mss_direction = self._extract_latest_direction([mss_analysis] if mss_analysis is not None else [])

        if normalized and ("range" in normalized or "side" in normalized):
            if mss_direction in {"up", "down"}:
                return mss_direction
            if bos_direction in {"up", "down"}:
                return bos_direction
            return "side"

        if bos_direction == mss_direction and bos_direction in {"up", "down"}:
            return bos_direction
        if bos_direction in {"up", "down"}:
            return bos_direction
        if mss_direction in {"up", "down"}:
            return mss_direction

        return "side"

    def _extract_latest_direction(self, signals: Sequence[object]) -> str | None:
        if not signals:
            return None

        latest = signals[-1]
        direction = getattr(latest, "direction", None)
        if direction is None:
            direction = getattr(latest, "trend", None)
        if direction is None:
            direction = str(latest)
        direction = str(direction).lower()
        if "up" in direction:
            return "up"
        if "down" in direction:
            return "down"
        return None

    def _classify_trend_strength(
        self,
        direction: str,
        bos_confirmed: bool,
        mss_confirmed: bool,
        choch_confirmed: bool,
    ) -> TrendStrength:
        if direction == "side":
            return TrendStrength.SIDEWAYS

        if direction == "up":
            if bos_confirmed and mss_confirmed:
                strength = TrendStrength.VERY_BULLISH
            elif bos_confirmed:
                strength = TrendStrength.BULLISH
            elif mss_confirmed:
                strength = TrendStrength.WEAK_BULLISH
            else:
                strength = TrendStrength.WEAK_BULLISH
        else:
            if bos_confirmed and mss_confirmed:
                strength = TrendStrength.VERY_BEARISH
            elif bos_confirmed:
                strength = TrendStrength.BEARISH
            elif mss_confirmed:
                strength = TrendStrength.WEAK_BEARISH
            else:
                strength = TrendStrength.WEAK_BEARISH

        if choch_confirmed:
            if strength == TrendStrength.VERY_BULLISH:
                return TrendStrength.BULLISH
            if strength == TrendStrength.BULLISH:
                return TrendStrength.WEAK_BULLISH
            if strength == TrendStrength.WEAK_BULLISH:
                return TrendStrength.SIDEWAYS
            if strength == TrendStrength.VERY_BEARISH:
                return TrendStrength.BEARISH
            if strength == TrendStrength.BEARISH:
                return TrendStrength.WEAK_BEARISH
            if strength == TrendStrength.WEAK_BEARISH:
                return TrendStrength.SIDEWAYS

        return strength

    def _calculate_confidence(
        self,
        bos_confirmed: bool,
        choch_confirmed: bool,
        mss_confirmed: bool,
        direction: str,
        bos_signals: Sequence[object],
        mss_analysis: object | None,
    ) -> float:
        if direction == "side" and not bos_confirmed and not mss_confirmed:
            return 0.0

        confidence = 0.2
        if bos_confirmed:
            confidence += 0.2
        if mss_confirmed:
            confidence += 0.2
        if bos_confirmed and mss_confirmed and self._directions_agree(bos_signals, mss_analysis):
            confidence += 0.15
        if choch_confirmed:
            confidence -= 0.15

        return max(0.0, min(1.0, confidence))

    def _directions_agree(self, bos_signals: Sequence[object], mss_analysis: object | None) -> bool:
        bos_direction = self._extract_latest_direction(bos_signals)
        mss_direction = self._extract_latest_direction([mss_analysis] if mss_analysis is not None else [])
        return bos_direction is not None and bos_direction == mss_direction

    def _extract_swing_prices(self, swings: Sequence[object], expected_type: str) -> list[float]:
        prices: list[float] = []
        for swing in swings:
            swing_type = getattr(swing, "type", None)
            swing_direction = getattr(swing, "direction", None)
            price = getattr(swing, "price", None)
            if price is None and hasattr(swing, "end_price"):
                price = getattr(swing, "end_price")
            if price is None:
                continue

            normalized_type = str(swing_type).lower() if swing_type is not None else ""
            normalized_direction = str(swing_direction).lower() if swing_direction is not None else ""
            if expected_type == "high" and ("high" in normalized_type or normalized_direction == "down"):
                prices.append(float(price))
            if expected_type == "low" and ("low" in normalized_type or normalized_direction == "up"):
                prices.append(float(price))

        return prices

    def _latest_timestamp(
        self,
        bos_signals: Sequence[object],
        choch_signals: Sequence[object],
        mss_analysis: object | None,
        swings: Sequence[object],
    ) -> datetime:
        candidates: list[datetime] = []

        for signal in (*bos_signals, *choch_signals, *swings):
            timestamp = getattr(signal, "timestamp", None)
            if isinstance(timestamp, datetime):
                candidates.append(timestamp)

        if mss_analysis is not None:
            timestamp = getattr(mss_analysis, "timestamp", None)
            if isinstance(timestamp, datetime):
                candidates.append(timestamp)

        return max(candidates) if candidates else datetime(1970, 1, 1)
