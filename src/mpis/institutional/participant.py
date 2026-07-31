"""Participant helpers for institutional psychology in MPIS."""
from __future__ import annotations

from dataclasses import dataclass

from mpis.institutional.models import ParticipantRecord


@dataclass(frozen=True)
class ParticipantHelper:
    """Helper class for participant record calculations."""

    record: ParticipantRecord

    def net_equity(self) -> float:
        """Return net equity flow."""
        return self.record.equity_buy - self.record.equity_sell

    def net_future(self) -> float:
        """Return net future flow."""
        return self.record.future_buy - self.record.future_sell

    def net_option(self) -> float:
        """Return net option flow."""
        return self.record.option_buy - self.record.option_sell

    def net_position(self) -> float:
        """Return overall net position across asset classes."""
        return self.net_equity() + self.net_future() + self.net_option()

    def is_buyer(self) -> bool:
        """Return True when net position is positive."""
        return self.net_position() > 0.0

    def is_seller(self) -> bool:
        """Return True when net position is negative."""
        return self.net_position() < 0.0
