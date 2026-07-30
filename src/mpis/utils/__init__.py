"""Utility helpers for MPIS."""
from pathlib import Path
from typing import Iterable


def ensure_dirs(paths: Iterable[Path]) -> None:
    """Ensure that each path in ``paths`` exists as a directory.

    Args:
        paths: Iterable of Path objects to create if missing.
    """
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
