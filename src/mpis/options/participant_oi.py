"""Participant-level open interest helper logic for MPIS."""
from __future__ import annotations

from dataclasses import dataclass

from mpis.options.models import ParticipantOIRecord


@dataclass(frozen=True)
class ParticipantOIHelper:
    """Helper for participant open interest record computations."""

    record: ParticipantOIRecord

    def position_balance(self) -> float:
        """Return the net long/short balance for the participant."""
        return self.record.long_oi - self.record.short_oi

    def change_balance(self) -> float:
        """Return the net change in open interest for the participant."""
        return self.record.long_change - self.record.short_change

    def is_increasing_long(self) -> bool:
        """Return whether the participant is building a long position."""
        return self.record.long_oi > 0.0 and self.record.long_change > 0.0

    def is_increasing_short(self) -> bool:
        """Return whether the participant is building a short position."""
        return self.record.short_oi > 0.0 and self.record.short_change > 0.0

    def is_unwinding_long(self) -> bool:
        """Return whether the participant is reducing long exposure."""
        return self.record.long_oi > 0.0 and self.record.long_change < 0.0

    def is_covering_short(self) -> bool:
        """Return whether the participant is covering shorts."""
        return self.record.short_oi > 0.0 and self.record.short_change < 0.0

    def is_trapped_long(self) -> bool:
        """Return whether a long participant may be trapped by falling OI."""
        return self.record.net_oi > 0.0 and self.record.long_change < 0.0

    def is_trapped_short(self) -> bool:
        """Return whether a short participant may be trapped by covering activity."""
        return self.record.net_oi < 0.0 and self.record.short_change < 0.0

    def has_conviction(self) -> bool:
        """Return True when the participant displays strong open interest conviction."""
        return abs(self.change_balance()) >= 1000.0 and self.record.volume >= 10000.0

    def conviction_score(self) -> float:
        """Return a conviction score proportional to changes and volume."""
        score = abs(self.change_balance()) * 0.0001 + self.record.volume * 0.00001
        if self.has_conviction():
            score *= 1.2
        return score
