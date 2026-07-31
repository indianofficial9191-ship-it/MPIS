from datetime import datetime

from mpis.data.buffer import ReplayBuffer
from mpis.data.candle import Candle
from mpis.structure.models import SwingStrength, SwingType
from mpis.structure.swings import SwingDetector


def build_buffer(candles_data):
    candles = [
        Candle(
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            symbol="TEST",
            timeframe="1m",
        )
        for timestamp, open_price, high_price, low_price, close_price in candles_data
    ]
    return ReplayBuffer(candles)


def test_detects_a_swing_high() -> None:
    buffer = build_buffer(
        [
            (datetime(2026, 7, 31, 12, 0), 100.0, 101.0, 99.0, 100.0),
            (datetime(2026, 7, 31, 12, 1), 100.0, 105.0, 99.0, 103.0),
            (datetime(2026, 7, 31, 12, 2), 104.0, 110.0, 103.0, 109.0),
            (datetime(2026, 7, 31, 12, 3), 109.0, 109.0, 105.0, 105.0),
            (datetime(2026, 7, 31, 12, 4), 105.0, 107.0, 104.0, 106.0),
        ]
    )
    detector = SwingDetector(left_bars=1, right_bars=1)
    swings = detector.detect(buffer)

    assert len(swings) == 1
    assert swings[0].type == SwingType.HIGH
    assert swings[0].price == 110.0
    assert swings[0].strength in {SwingStrength.WEAK, SwingStrength.STRONG}


def test_detects_a_swing_low() -> None:
    buffer = build_buffer(
        [
            (datetime(2026, 7, 31, 12, 0), 105.0, 108.0, 103.0, 107.0),
            (datetime(2026, 7, 31, 12, 1), 107.0, 110.0, 106.0, 109.0),
            (datetime(2026, 7, 31, 12, 2), 109.0, 111.0, 104.0, 105.0),
            (datetime(2026, 7, 31, 12, 3), 105.0, 108.0, 105.0, 107.0),
            (datetime(2026, 7, 31, 12, 4), 107.0, 109.0, 106.0, 108.0),
        ]
    )
    detector = SwingDetector(left_bars=1, right_bars=1)
    swings = detector.detect(buffer)

    assert len(swings) == 1
    assert swings[0].type == SwingType.LOW
    assert swings[0].price == 104.0


def test_returns_empty_list_on_flat_data() -> None:
    buffer = build_buffer(
        [
            (datetime(2026, 7, 31, 12, 0), 100.0, 100.0, 100.0, 100.0),
            (datetime(2026, 7, 31, 12, 1), 100.0, 100.0, 100.0, 100.0),
            (datetime(2026, 7, 31, 12, 2), 100.0, 100.0, 100.0, 100.0),
            (datetime(2026, 7, 31, 12, 3), 100.0, 100.0, 100.0, 100.0),
            (datetime(2026, 7, 31, 12, 4), 100.0, 100.0, 100.0, 100.0),
        ]
    )
    detector = SwingDetector(left_bars=1, right_bars=1)
    swings = detector.detect(buffer)

    assert swings == []


def test_ignores_edge_candles() -> None:
    buffer = build_buffer(
        [
            (datetime(2026, 7, 31, 12, 0), 100.0, 110.0, 100.0, 105.0),
            (datetime(2026, 7, 31, 12, 1), 105.0, 106.0, 104.0, 105.0),
            (datetime(2026, 7, 31, 12, 2), 105.0, 107.0, 104.0, 106.0),
            (datetime(2026, 7, 31, 12, 3), 106.0, 108.0, 105.0, 107.0),
            (datetime(2026, 7, 31, 12, 4), 107.0, 109.0, 106.0, 108.0),
        ]
    )
    detector = SwingDetector(left_bars=2, right_bars=2)
    swings = detector.detect(buffer)

    assert swings == []


def test_returns_swings_ordered_by_index() -> None:
    buffer = build_buffer(
        [
            (datetime(2026, 7, 31, 12, 0), 100.0, 101.0, 99.0, 100.0),
            (datetime(2026, 7, 31, 12, 1), 100.0, 102.0, 99.0, 101.0),
            (datetime(2026, 7, 31, 12, 2), 101.0, 103.0, 100.0, 102.0),
            (datetime(2026, 7, 31, 12, 3), 102.0, 105.0, 101.0, 104.0),
            (datetime(2026, 7, 31, 12, 4), 103.0, 104.0, 99.0, 100.0),
            (datetime(2026, 7, 31, 12, 5), 100.0, 102.0, 98.0, 101.0),
            (datetime(2026, 7, 31, 12, 6), 101.0, 103.0, 97.0, 102.0),
            (datetime(2026, 7, 31, 12, 7), 102.0, 104.0, 100.0, 103.0),
            (datetime(2026, 7, 31, 12, 8), 103.0, 107.0, 101.0, 106.0),
            (datetime(2026, 7, 31, 12, 9), 106.0, 108.0, 105.0, 107.0),
        ]
    )
    detector = SwingDetector(left_bars=1, right_bars=1)
    swings = detector.detect(buffer)

    assert len(swings) >= 2
    assert [s.index for s in swings] == sorted(s.index for s in swings)
