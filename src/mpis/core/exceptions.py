"""Exception hierarchy for MPIS core infrastructure."""
from __future__ import annotations

from typing import Type


class MPISError(Exception):
    """Base exception for MPIS infrastructure errors."""


class ConfigurationError(MPISError):
    """Raised when configuration validation or loading fails."""


class ReplayError(MPISError):
    """Raised for errors in replay processing or playback."""


class RuleEngineError(MPISError):
    """Raised for rule execution or rule management failures."""


class FusionError(MPISError):
    """Raised when fusion or aggregation processing fails."""


class DashboardError(MPISError):
    """Raised for dashboard rendering or dashboard integration failures."""


class InstitutionError(MPISError):
    """Raised for errors in institutional data or institutional logic."""


class OptionsError(MPISError):
    """Raised when option parsing or option validation fails."""


class AIEngineError(MPISError):
    """Raised for AI model integration or inference failures."""


class ValidationError(MPISError):
    """Raised when a model or business validation fails."""


class DataError(MPISError):
    """Raised for problems with data quality, transformations, or ingestion."""
