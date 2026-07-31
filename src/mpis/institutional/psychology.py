"""Institutional psychology heuristics for MPIS."""
from __future__ import annotations

from typing import Sequence

from mpis.institutional.models import MarketState, ParticipantRecord
from mpis.institutional.participant import ParticipantHelper


class PsychologyEngine:
    """Psychology engine for detecting institutional market conditions."""

    @staticmethod
    def detect_long_buildup(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when institutional buying momentum is strong."""
        score = 0.0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_equity() > 0 and helper.net_future() > 0:
                score += helper.net_position()
        return score > 1_000_000.0

    @staticmethod
    def detect_short_buildup(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when institutional shorting momentum is strong."""
        score = 0.0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_equity() < 0 and helper.net_future() < 0:
                score += abs(helper.net_position())
        return score > 1_000_000.0

    @staticmethod
    def detect_long_unwinding(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when long positions are being reduced."""
        score = 0.0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_equity() < 0 and helper.net_option() < 0:
                score += abs(helper.net_position())
        return score > 750_000.0

    @staticmethod
    def detect_short_covering(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when short positions are being covered."""
        score = 0.0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_equity() > 0 and helper.net_option() > 0:
                score += helper.net_position()
        return score > 750_000.0

    @staticmethod
    def detect_accumulation(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when participants are accumulating shares."""
        positive = 0
        negative = 0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_position() > 0:
                positive += 1
            if helper.net_position() < 0:
                negative += 1
        return positive > negative and positive >= 2

    @staticmethod
    def detect_distribution(participants: Sequence[ParticipantRecord]) -> bool:
        """Return True when participants are distributing shares."""
        positive = 0
        negative = 0
        for record in participants:
            helper = ParticipantHelper(record)
            if helper.net_position() > 0:
                positive += 1
            if helper.net_position() < 0:
                negative += 1
        return negative > positive and negative >= 2
