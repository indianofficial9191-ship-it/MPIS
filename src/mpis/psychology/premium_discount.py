"""Premium/discount analysis for MPIS psychology sprint 5.2."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ZoneType(str, Enum):
    """Pricing zones based on equilibrium reference."""

    PREMIUM = "premium"
    EQUILIBRIUM = "equilibrium"
    DISCOUNT = "discount"


@dataclass(frozen=True)
class PremiumDiscountAnalysis:
    """Result of premium/discount analysis."""

    current_price: float
    swing_high: float
    swing_low: float
    equilibrium: float
    zone: ZoneType
    premium_percent: float
    discount_percent: float


class PremiumDiscountEngine:
    """Engine to analyze price premium and discount relative to swing boundaries."""

    def analyze(
        self,
        current_price: float,
        swing_high: float,
        swing_low: float,
    ) -> PremiumDiscountAnalysis:
        """Analyze the price relative to swing high/low and return the premium/discount context."""
        if swing_high < swing_low:
            raise ValueError("swing_high must be greater than or equal to swing_low")

        equilibrium = (swing_high + swing_low) / 2.0
        if current_price > equilibrium:
            zone = ZoneType.PREMIUM
        elif current_price < equilibrium:
            zone = ZoneType.DISCOUNT
        else:
            zone = ZoneType.EQUILIBRIUM

        range_size = swing_high - swing_low
        if range_size <= 0.0:
            premium_percent = 0.0
            discount_percent = 0.0
        elif zone == ZoneType.PREMIUM:
            premium_percent = ((current_price - equilibrium) / range_size) * 100.0
            discount_percent = 0.0
        elif zone == ZoneType.DISCOUNT:
            premium_percent = 0.0
            discount_percent = ((equilibrium - current_price) / range_size) * 100.0
        else:
            premium_percent = 0.0
            discount_percent = 0.0

        return PremiumDiscountAnalysis(
            current_price=current_price,
            swing_high=swing_high,
            swing_low=swing_low,
            equilibrium=equilibrium,
            zone=zone,
            premium_percent=round(premium_percent, 4),
            discount_percent=round(discount_percent, 4),
        )
