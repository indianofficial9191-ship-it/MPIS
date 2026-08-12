from __future__ import annotations

from .models import (
    TradingReadinessInput,
    TradingReadinessReason,
    TradingReadinessResult,
    TradingReadinessStatus,
)


class TradingReadinessEngine:
    """
    Final pre-trade readiness coordinator.

    This engine does NOT place orders.
    It only determines whether the live trading pipeline is ready.
    """

    def evaluate(
        self,
        request: TradingReadinessInput,
    ) -> TradingReadinessResult:
        symbol = request.symbol.upper()

        failed_checks: list[str] = []

        if not request.market_open:
            failed_checks.append("market_open")

        if not request.market_data_healthy:
            failed_checks.append("market_data_healthy")

        if not request.decision_ready:
            failed_checks.append("decision_ready")

        if not request.risk_allowed:
            failed_checks.append("risk_allowed")

        if not request.execution_ready:
            failed_checks.append("execution_ready")

        if not failed_checks:
            return TradingReadinessResult(
                status=TradingReadinessStatus.READY,
                ready=True,
                reason=TradingReadinessReason.ALL_CHECKS_PASSED,
                symbol=symbol,
                failed_checks=(),
            )

        reason = self._reason_for_failure(request)

        return TradingReadinessResult(
            status=TradingReadinessStatus.NOT_READY,
            ready=False,
            reason=reason,
            symbol=symbol,
            failed_checks=tuple(failed_checks),
        )

    @staticmethod
    def _reason_for_failure(
        request: TradingReadinessInput,
    ) -> TradingReadinessReason:
        if not request.market_open:
            return TradingReadinessReason.MARKET_CLOSED

        if not request.market_data_healthy:
            return TradingReadinessReason.MARKET_DATA_UNHEALTHY

        if not request.decision_ready:
            return TradingReadinessReason.DECISION_NOT_READY

        if not request.risk_allowed:
            return TradingReadinessReason.RISK_GUARD_BLOCKED

        if not request.execution_ready:
            return TradingReadinessReason.EXECUTION_NOT_READY

        return TradingReadinessReason.MARKET_SESSION_INVALID