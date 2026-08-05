"""Psychological level analysis for MPIS."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mpis.psychology.models import (
    AboveBelow,
    PsychologicalLevelResult,
    PsychologicalLevelsConfig,
)


DEFAULT_SYMBOL_STEPS: dict[str, Sequence[int]] = {
    "NIFTY": (100,),
    "BANKNIFTY": (500, 1000),
}


@dataclass(frozen=True)
class PsychologicalLevelsAnalyzer:
    """Analyze price levels against configurable psychological numbers."""

    symbol: str | None = None
    steps: Sequence[int] | None = None
    zone_width: float = 25.0

    def analyze(self, price: float) -> list[PsychologicalLevelResult]:
        """Return psychological level results for a price."""
        symbol = self.symbol or ""
        if self.steps is None:
            if not symbol:
                raise ValueError("Symbol or steps must be configured for psychological levels analysis.")
            symbol = symbol.upper()
            steps = DEFAULT_SYMBOL_STEPS.get(symbol)
            if steps is None:
                raise ValueError(
                    f"Unsupported symbol '{symbol}'; supported symbols are: {', '.join(DEFAULT_SYMBOL_STEPS)}"
                )
        else:
            steps = self.steps

        if self.zone_width <= 0:
            raise ValueError("zone_width must be positive")

        results: list[PsychologicalLevelResult] = []
        for step in steps:
            if step <= 0:
                raise ValueError("step must be positive")
            nearest_level = round(price / step) * step
            distance = abs(price - nearest_level)
            if price > nearest_level:
                above_or_below = AboveBelow.ABOVE
            elif price < nearest_level:
                above_or_below = AboveBelow.BELOW
            else:
                above_or_below = AboveBelow.AT

            strength_score = max(0.0, min(1.0, 1.0 - distance / self.zone_width))
            zone_low = nearest_level - self.zone_width
            zone_high = nearest_level + self.zone_width

            results.append(
                PsychologicalLevelResult(
                    symbol=symbol,
                    step=step,
                    nearest_level=float(nearest_level),
                    distance=float(distance),
                    above_or_below=above_or_below,
                    strength_score=round(strength_score, 4),
                    zone_low=float(zone_low),
                    zone_high=float(zone_high),
                )
            )

        return results
