"""MPIS configuration package.

Expose a singleton `settings` object for the rest of the application.
"""
from __future__ import annotations

from .settings import load_settings, Settings

# Create the singleton settings instance on import using defaults. Other
# modules should `from mpis.config import settings` and read attributes.
settings: Settings = load_settings()

__all__ = ["settings", "Settings"]

