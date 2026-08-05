from datetime import datetime

from mpis.data.candle import Candle
from mpis.psychology.models import WickAnalysisClassification
from mpis.psychology.wick_analysis import WickAnalyzer


def _candle(ts: datetime, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(timestamp=ts, open=open_price, high=high, low=low, close=close, symbol="TEST", timeframe="1m")


def test_bullish_rejection_classification() -> None:
    candle = _candle(datetime(2026, 8, 5, 9, 15), 100.0, 101.0, 98.0, 100.5)
    result = WickAnalyzer().analyze(candle)

    assert result.classification == WickAnalysisClassification.BULLISH_REJECTION
    assert result.lower_wick_pct >= 40.0


def test_bearish_rejection_classification() -> None:
    candle = _candle(datetime(2026, 8, 5, 9, 15), 106.0, 110.0, 104.0, 105.0)
    result = WickAnalyzer().analyze(candle)

    assert result.classification == WickAnalysisClassification.BEARISH_REJECTION
    assert result.upper_wick_pct >= 40.0


def test_neutral_wick_classification() -> None:
    candle = _candle(datetime(2026, 8, 5, 9, 15), 200.0, 201.0, 199.0, 200.0)
    result = WickAnalyzer().analyze(candle)

    assert result.classification == WickAnalysisClassification.NEUTRAL


def test_wick_percentages_sum_within_range() -> None:
    candle = _candle(datetime(2026, 8, 5, 9, 15), 120.0, 123.0, 119.0, 121.0)
    result = WickAnalyzer().analyze(candle)

    assert 0.0 <= result.upper_wick_pct <= 100.0
    assert 0.0 <= result.lower_wick_pct <= 100.0
    assert 0.0 <= result.body_pct <= 100.0


def test_wick_analysis_handles_flat_range() -> None:
    candle = _candle(datetime(2026, 8, 5, 9, 15), 50.0, 50.0, 50.0, 50.0)
    result = WickAnalyzer().analyze(candle)

    assert result.upper_wick_pct == 0.0
    assert result.lower_wick_pct == 0.0
    assert result.body_pct == 0.0
    assert result.classification == WickAnalysisClassification.NEUTRAL
