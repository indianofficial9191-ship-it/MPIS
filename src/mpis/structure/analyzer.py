"""Market structure analysis for swing detection in MPIS."""
from __future__ import annotations

from collections.abc import Sequence
import pandas as pd

from mpis.structure.models import Swing
from mpis.structure.swings import SwingDetector
from mpis.utils.logger import get_logger


class MarketStructureAnalyzer:
    """Analyze market structure by detecting swings in price data."""

    def __init__(self) -> None:
        self.logger = get_logger("mpis.structure.analyzer")

    def analyze(self, dataframe: pd.DataFrame, lookback: int = 2) -> list[Swing]:
        """Detect swings in the given OHLC time series DataFrame."""
        self.logger.info("Starting market structure analysis", extra={"rows": len(dataframe), "lookback": lookback})
        swings = SwingDetector.detect_swings(dataframe, lookback=lookback)
        self.logger.info("Market structure analysis complete", extra={"swing_count": len(swings)})
        return swings
