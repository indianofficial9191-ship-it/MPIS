"""Long/short comparisons used for open interest analysis in MPIS."""
from __future__ import annotations

from mpis.options.models import Direction


def infer_direction(long_change: float, short_change: float) -> Direction:
    """Infer the market direction from long and short open interest changes."""
    if long_change > 0.0 and short_change > 0.0:
        return Direction.NEUTRAL
    if long_change > 0.0 and short_change <= 0.0:
        return Direction.BULLISH
    if long_change <= 0.0 and short_change > 0.0:
        return Direction.BEARISH
    return Direction.NEUTRAL
