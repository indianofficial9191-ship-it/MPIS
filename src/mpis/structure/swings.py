"""Swing detection utilities for market structure analysis in MPIS."""
from __future__ import annotations

from collections.abc import Sequence

from mpis.data.buffer import ReplayBuffer
from mpis.structure.models import SwingPoint, SwingStrength, SwingType


class SwingDetector:
    """Detect swing points from a replay candle buffer."""

    def __init__(self, left_bars: int = 3, right_bars: int = 3) -> None:
        if left_bars < 1 or right_bars < 1:
            raise ValueError("left_bars and right_bars must be at least 1")
        self.left_bars = left_bars
        self.right_bars = right_bars

    def detect(self, buffer: ReplayBuffer) -> list[SwingPoint]:
        """Detect swing high and swing low points from replay data."""
        swings: list[SwingPoint] = []
        total_candles = len(buffer)
        start_index = self.left_bars
        end_index = total_candles - self.right_bars

        for index in range(start_index, end_index):
            current = buffer[index]
            previous_candles = [buffer[i] for i in range(index - self.left_bars, index)]
            next_candles = [buffer[i] for i in range(index + 1, index + self.right_bars + 1)]

            previous_highs = [c.high for c in previous_candles]
            next_highs = [c.high for c in next_candles]
            previous_lows = [c.low for c in previous_candles]
            next_lows = [c.low for c in next_candles]

            is_swing_high = (
                current.high > max(previous_highs)
                and current.high > max(next_highs)
            )
            is_swing_low = (
                current.low < min(previous_lows)
                and current.low < min(next_lows)
            )

            if is_swing_low:
                swings.append(
                    SwingPoint(
                        index=index,
                        timestamp=current.timestamp,
                        price=current.low,
                        type=SwingType.LOW,
                        strength=self._measure_strength(current.low, previous_lows, next_lows),
                    )
                )
            elif is_swing_high:
                swings.append(
                    SwingPoint(
                        index=index,
                        timestamp=current.timestamp,
                        price=current.high,
                        type=SwingType.HIGH,
                        strength=self._measure_strength(current.high, previous_highs, next_highs),
                    )
                )

        return sorted(swings, key=lambda swing: swing.index)

    @staticmethod
    def _measure_strength(value: float, previous_values: Sequence[float], next_values: Sequence[float]) -> SwingStrength:
        """Measure whether a swing point is weak or strong."""
        previous_gap = value - max(previous_values)
        next_gap = value - max(next_values)
        average_gap = (previous_gap + next_gap) / 2.0
        threshold = 0.5 * max(max(previous_values) - min(previous_values), max(next_values) - min(next_values), 1.0)
        return SwingStrength.STRONG if average_gap >= threshold else SwingStrength.WEAK
