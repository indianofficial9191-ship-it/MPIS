from datetime import datetime

import pandas as pd
import pytest

from mpis.institutional.orderflow import OrderFlowAnalyzer


def sample_frame():
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01 09:15", periods=5, freq="min"),
            "open": [100, 100, 100, 101, 101],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 99, 99, 100, 100],
            "close": [100.8, 101.8, 102.8, 103.8, 104.8],
            "volume": [100, 110, 150, 180, 200],
        }
    )


def test_orderflow_summary_is_deterministic():
    analyzer = OrderFlowAnalyzer()
    first = analyzer.analyze(sample_frame())
    second = analyzer.analyze(sample_frame())

    assert first == second
    assert first.bars_analyzed == 5
    assert 0 <= first.absorption_score <= 1
    assert 0 <= first.imbalance_score <= 1
    assert 0 <= first.institutional_score <= 1


def test_bullish_sequence_has_positive_delta():
    summary = OrderFlowAnalyzer().analyze(sample_frame())
    assert summary.delta_proxy > 0
    assert summary.dominant_side == "BUY"


def test_missing_columns_fail_fast():
    with pytest.raises(ValueError, match="Missing required OHLCV columns"):
        OrderFlowAnalyzer().analyze(pd.DataFrame({"close": [1, 2]}))


def test_empty_frame_returns_neutral_summary():
    frame = sample_frame().iloc[0:0]
    summary = OrderFlowAnalyzer().analyze(frame)

    assert summary.bars_analyzed == 0
    assert summary.dominant_side == "NEUTRAL"
    assert summary.institutional_score == 0.0
