"""Project-wide constants for configuration subsystem."""
from __future__ import annotations

from datetime import time
from enum import Enum
from pathlib import Path


class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class MarketProfileEnum(str, Enum):
    NIFTY = "nifty"
    BANKNIFTY = "banknifty"


class ModeEnum(str, Enum):
    REPLAY = "replay"
    LIVE = "live"
    PAPER = "paper"


PROJECT_CONFIG_DIR = Path("configs")
DEFAULT_CONFIG_FILES = [
    PROJECT_CONFIG_DIR / "default.yaml",
    PROJECT_CONFIG_DIR / "development.yaml",
]

# Timezone and market hours (naive times; systems should localize as needed)
DEFAULT_TIMEZONE = "Asia/Kolkata"
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

SUPPORTED_ENVIRONMENTS = [e.value for e in EnvironmentEnum]
SUPPORTED_MARKETS = [m.value for m in MarketProfileEnum]
SUPPORTED_MODES = [mm.value for mm in ModeEnum]
