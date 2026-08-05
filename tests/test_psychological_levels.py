import pytest

from mpis.psychology.psychological_levels import PsychologicalLevelsAnalyzer
from mpis.psychology.models import AboveBelow


def test_nifty_nearest_level_and_zone_bounds() -> None:
    analyzer = PsychologicalLevelsAnalyzer(symbol="NIFTY", zone_width=25.0)
    result = analyzer.analyze(17923.0)[0]

    assert result.step == 100
    assert result.nearest_level == 17900.0
    assert result.zone_low == 17875.0
    assert result.zone_high == 17925.0
    assert result.above_or_below == AboveBelow.ABOVE
    assert result.distance == 23.0
    assert result.strength_score == 0.08


def test_nifty_price_on_level_returns_at_strength_one() -> None:
    analyzer = PsychologicalLevelsAnalyzer(symbol="nifty", zone_width=50.0)
    result = analyzer.analyze(18100.0)[0]

    assert result.nearest_level == 18100.0
    assert result.above_or_below == AboveBelow.AT
    assert result.strength_score == 1.0


def test_banknifty_supports_multiple_steps() -> None:
    analyzer = PsychologicalLevelsAnalyzer(symbol="BANKNIFTY", zone_width=100.0)
    results = analyzer.analyze(51475.0)

    assert len(results) == 2
    assert {result.step for result in results} == {500, 1000}
    high_step = next(result for result in results if result.step == 1000)
    assert high_step.nearest_level == 51000.0
    assert high_step.above_or_below == AboveBelow.ABOVE
    assert high_step.zone_low == 50900.0
    assert high_step.zone_high == 51100.0


def test_custom_steps_can_be_provided_without_symbol() -> None:
    analyzer = PsychologicalLevelsAnalyzer(steps=(250, 750), zone_width=10.0)
    results = analyzer.analyze(1010.0)

    assert len(results) == 2
    assert results[0].step == 250
    assert results[1].step == 750
    assert results[0].nearest_level == 1000.0
    assert results[1].nearest_level == 750.0


def test_invalid_zone_width_and_step_raise_value_error() -> None:
    with pytest.raises(ValueError):
        PsychologicalLevelsAnalyzer(symbol="NIFTY", zone_width=0.0).analyze(18000.0)
