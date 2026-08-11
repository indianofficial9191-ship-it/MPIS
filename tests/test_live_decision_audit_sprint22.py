"""Sprint 22 live decision audit ledger tests."""

from datetime import datetime, timezone

import pytest

from mpis.live.audit import (
    AuditDecision,
    AuditEvent,
    LiveDecisionAuditLedger,
)


def test_record_and_retrieve_event():
    ledger = LiveDecisionAuditLedger()

    event = AuditEvent(
        symbol="NIFTY",
        action=AuditDecision.BUY,
        confidence=0.82,
        accepted=True,
        reason="Aligned live decision",
        timestamp=datetime.now(timezone.utc),
        source="live_decision_orchestration",
    )

    event_id = ledger.record(event)

    assert event_id == 1
    assert ledger.count() == 1

    stored = ledger.get(event_id)

    assert stored is not None
    assert stored.symbol == "NIFTY"
    assert stored.action is AuditDecision.BUY
    assert stored.confidence == 0.82
    assert stored.accepted is True


def test_sequential_event_ids():
    ledger = LiveDecisionAuditLedger()

    for index in range(3):
        event = AuditEvent(
            symbol="BANKNIFTY",
            action=AuditDecision.SELL,
            confidence=0.70 + index * 0.05,
            accepted=True,
            reason="Bearish alignment",
            timestamp=datetime.now(timezone.utc),
            source="live_decision_orchestration",
        )

        assert ledger.record(event) == index + 1

    assert ledger.count() == 3


def test_rejected_decision_is_recorded():
    ledger = LiveDecisionAuditLedger()

    event = AuditEvent(
        symbol="NIFTY",
        action=AuditDecision.BUY,
        confidence=0.61,
        accepted=False,
        reason="Confidence below threshold",
        timestamp=datetime.now(timezone.utc),
        source="live_decision_orchestration",
    )

    event_id = ledger.record(event)
    stored = ledger.get(event_id)

    assert stored is not None
    assert stored.accepted is False
    assert stored.reason == "Confidence below threshold"


def test_invalid_confidence_is_rejected():
    ledger = LiveDecisionAuditLedger()

    with pytest.raises(ValueError):
        ledger.record(
            AuditEvent(
                symbol="NIFTY",
                action=AuditDecision.BUY,
                confidence=1.2,
                accepted=True,
                reason="Invalid confidence",
                timestamp=datetime.now(timezone.utc),
                source="test",
            )
        )


def test_negative_confidence_is_rejected():
    ledger = LiveDecisionAuditLedger()

    with pytest.raises(ValueError):
        ledger.record(
            AuditEvent(
                symbol="NIFTY",
                action=AuditDecision.SELL,
                confidence=-0.1,
                accepted=False,
                reason="Invalid confidence",
                timestamp=datetime.now(timezone.utc),
                source="test",
            )
        )


def test_events_are_returned_in_record_order():
    ledger = LiveDecisionAuditLedger()

    for symbol in ("NIFTY", "BANKNIFTY", "NIFTY"):
        ledger.record(
            AuditEvent(
                symbol=symbol,
                action=AuditDecision.HOLD,
                confidence=0.5,
                accepted=False,
                reason="No actionable setup",
                timestamp=datetime.now(timezone.utc),
                source="test",
            )
        )

    events = ledger.events()

    assert len(events) == 3
    assert [event.symbol for event in events] == [
        "NIFTY",
        "BANKNIFTY",
        "NIFTY",
    ]


def test_clear_removes_all_events():
    ledger = LiveDecisionAuditLedger()

    ledger.record(
        AuditEvent(
            symbol="NIFTY",
            action=AuditDecision.BUY,
            confidence=0.8,
            accepted=True,
            reason="Test",
            timestamp=datetime.now(timezone.utc),
            source="test",
        )
    )

    assert ledger.count() == 1

    ledger.clear()

    assert ledger.count() == 0
    assert ledger.get(1) is None


def test_unknown_event_returns_none():
    ledger = LiveDecisionAuditLedger()

    assert ledger.get(999) is None
