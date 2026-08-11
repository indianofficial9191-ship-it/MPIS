"""Sprint 20 live integration engine."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import LiveIntegrationResult


class LiveIntegrationEngine:
    """Final safety/integration gate for live signals."""

    MIN_CONFIDENCE = 0.70
    MAX_SIGNAL_AGE_SECONDS = 60.0
    SUPPORTED_SYMBOLS = {"NIFTY", "BANKNIFTY"}
    SUPPORTED_ACTIONS = {"BUY", "SELL", "HOLD"}

    def process(
        self,
        symbol: str = "NIFTY",
        action: str = "HOLD",
        confidence: float = 0.0,
        ready: bool = True,
        execution_allowed: bool = True,
        timestamp: datetime | None = None,
    ) -> LiveIntegrationResult:
        if not symbol:
            raise ValueError("symbol must not be empty")

        if symbol not in self.SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {symbol}")

        if action not in self.SUPPORTED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        if timestamp is not None:
            now = datetime.now(timezone.utc)

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            age = (now - timestamp).total_seconds()

            if age > self.MAX_SIGNAL_AGE_SECONDS:
                return LiveIntegrationResult(
                    symbol=symbol,
                    action="HOLD",
                    confidence=confidence,
                    blocked=True,
                    reason="Stale signal rejected",
                    timestamp=timestamp,
                )

            if age < 0:
                return LiveIntegrationResult(
                    symbol=symbol,
                    action="HOLD",
                    confidence=confidence,
                    blocked=True,
                    reason="Future-dated signal rejected",
                    timestamp=timestamp,
                )

        if action == "HOLD":
            return LiveIntegrationResult(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                blocked=False,
                reason="No trade signal",
                timestamp=timestamp,
            )

        if confidence < self.MIN_CONFIDENCE:
            return LiveIntegrationResult(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                blocked=True,
                reason="Confidence below minimum threshold",
                timestamp=timestamp,
            )

        if not ready:
            return LiveIntegrationResult(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                blocked=True,
                reason="Live decision readiness check failed",
                timestamp=timestamp,
            )

        if not execution_allowed:
            return LiveIntegrationResult(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                blocked=True,
                reason="Execution guard blocked signal",
                timestamp=timestamp,
            )

        return LiveIntegrationResult(
            symbol=symbol,
            action=action,
            confidence=confidence,
            blocked=False,
            reason="Live signal accepted",
            timestamp=timestamp,
        )
