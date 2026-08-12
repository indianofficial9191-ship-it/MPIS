from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TradingReadinessStatus(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class TradingReadinessReason(str, Enum):
    ALL_CHECKS_PASSED = "ALL_CHECKS_PASSED"
    MARKET_CLOSED = "MARKET_CLOSED"
    MARKET_SESSION_INVALID = "MARKET_SESSION_INVALID"
    MARKET_DATA_UNHEALTHY = "MARKET_DATA_UNHEALTHY"
    DECISION_NOT_READY = "DECISION_NOT_READY"
    RISK_GUARD_BLOCKED = "RISK_GUARD_BLOCKED"
    EXECUTION_NOT_READY = "EXECUTION_NOT_READY"


@dataclass(frozen=True)
class TradingReadinessInput:
    symbol: str
    market_open: bool
    market_data_healthy: bool
    decision_ready: bool
    risk_allowed: bool
    execution_ready: bool


@dataclass(frozen=True)
class TradingReadinessResult:
    status: TradingReadinessStatus
    ready: bool
    reason: TradingReadinessReason
    symbol: str
    failed_checks: tuple[str, ...]