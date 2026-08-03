"""Configuration models for liquidity detectors."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquiditySweepConfig:
    """Configuration for liquidity sweep detection."""

    lookback: int = 3
    minimum_sweep_distance: float = 1.0
    confirmation_candles: int = 1
    require_close_confirmation: bool = True
    require_wick_confirmation: bool = False
