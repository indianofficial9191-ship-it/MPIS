import pytest

from mpis.psychology.premium_discount import (
    PremiumDiscountAnalysis,
    PremiumDiscountEngine,
    ZoneType,
)


def test_premium_zone_when_price_above_equilibrium() -> None:
    engine = PremiumDiscountEngine()
    result = engine.analyze(current_price=115.0, swing_high=120.0, swing_low=100.0)

    assert isinstance(result, PremiumDiscountAnalysis)
    assert result.zone == ZoneType.PREMIUM
    assert result.equilibrium == 110.0
    assert result.premium_percent == 25.0
    assert result.discount_percent == 0.0


def test_discount_zone_when_price_below_equilibrium() -> None:
    engine = PremiumDiscountEngine()
    result = engine.analyze(current_price=90.0, swing_high=120.0, swing_low=100.0)

    assert result.zone == ZoneType.DISCOUNT
    assert result.equilibrium == 110.0
    assert result.discount_percent == 100.0
    assert result.premium_percent == 0.0


def test_equilibrium_zone_when_price_equals_equilibrium() -> None:
    engine = PremiumDiscountEngine()
    result = engine.analyze(current_price=105.0, swing_high=110.0, swing_low=100.0)

    assert result.zone == ZoneType.EQUILIBRIUM
    assert result.premium_percent == 0.0
    assert result.discount_percent == 0.0


def test_handles_equal_high_low_without_division_error() -> None:
    engine = PremiumDiscountEngine()
    result = engine.analyze(current_price=100.0, swing_high=100.0, swing_low=100.0)

    assert result.zone == ZoneType.EQUILIBRIUM
    assert result.equilibrium == 100.0
    assert result.premium_percent == 0.0
    assert result.discount_percent == 0.0


def test_handles_equal_high_low_with_price_above() -> None:
    engine = PremiumDiscountEngine()
    result = engine.analyze(current_price=101.0, swing_high=100.0, swing_low=100.0)

    assert result.zone == ZoneType.PREMIUM
    assert result.premium_percent == 0.0
    assert result.discount_percent == 0.0


def test_invalid_swing_high_lower_than_swing_low_raises_value_error() -> None:
    engine = PremiumDiscountEngine()

    with pytest.raises(ValueError):
        engine.analyze(current_price=100.0, swing_high=90.0, swing_low=100.0)
