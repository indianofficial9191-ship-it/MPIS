import pytest

from mpis.core import (
    AIEngineError,
    ConfigurationError,
    DashboardError,
    DataError,
    FusionError,
    InstitutionError,
    MPISError,
    OptionsError,
    ReplayError,
    RuleEngineError,
    ValidationError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(ConfigurationError, MPISError)
    assert issubclass(ReplayError, MPISError)
    assert issubclass(RuleEngineError, MPISError)
    assert issubclass(FusionError, MPISError)
    assert issubclass(DashboardError, MPISError)
    assert issubclass(InstitutionError, MPISError)
    assert issubclass(OptionsError, MPISError)
    assert issubclass(AIEngineError, MPISError)
    assert issubclass(ValidationError, MPISError)
    assert issubclass(DataError, MPISError)


def test_raise_specific_exception() -> None:
    with pytest.raises(DataError):
        raise DataError("invalid data payload")
