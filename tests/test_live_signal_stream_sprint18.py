"""Sprint 18 live signal stream tests."""

from datetime import datetime, timezone

import pytest

from mpis.live.signal_stream import (
    SignalAction,
    SignalEvent,
    SignalStreamEngine,
)


def make_event(
    signal_id: str = "sig-1",
    symbol: str = "NIFTY",
    action: SignalAction = SignalAction.BUY,
    confidence: float = 0.80,
) -> SignalEvent:
    return SignalEvent(
        signal_id=signal_id,
        symbol=symbol,
        action=action,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc),
    )


def test_publish_assigns_sequence() -> None:
    engine = SignalStreamEngine()

    assert engine.publish(make_event()) == 1
    assert engine.sequence == 1


def test_latest_signal_is_available() -> None:
    engine = SignalStreamEngine()

    event = make_event()
    engine.publish(event)

    assert engine.latest("NIFTY") == event


def test_latest_signal_replaces_previous_signal() -> None:
    engine = SignalStreamEngine()

    first = make_event("sig-1", confidence=0.70)
    second = make_event("sig-2", confidence=0.90)

    engine.publish(first)
    engine.publish(second)

    assert engine.latest("NIFTY") == second


def test_history_can_be_filtered_by_symbol() -> None:
    engine = SignalStreamEngine()

    engine.publish(make_event("n-1", "NIFTY"))
    engine.publish(make_event("b-1", "BANKNIFTY"))
    engine.publish(make_event("n-2", "NIFTY"))

    history = engine.history("NIFTY")

    assert len(history) == 2
    assert all(event.symbol == "NIFTY" for event in history)


def test_snapshot_reports_symbol_state() -> None:
    engine = SignalStreamEngine()

    event = make_event()
    engine.publish(event)

    snapshot = engine.snapshot("NIFTY")

    assert snapshot.symbol == "NIFTY"
    assert snapshot.latest == event
    assert snapshot.event_count == 1
    assert snapshot.sequence == 1


def test_history_is_bounded() -> None:
    engine = SignalStreamEngine(max_history=2)

    engine.publish(make_event("sig-1"))
    engine.publish(make_event("sig-2"))
    engine.publish(make_event("sig-3"))

    history = engine.history()

    assert len(history) == 2
    assert [event.signal_id for event in history] == ["sig-2", "sig-3"]


def test_invalid_confidence_is_rejected() -> None:
    engine = SignalStreamEngine()

    with pytest.raises(ValueError, match="confidence"):
        engine.publish(make_event(confidence=1.1))


def test_empty_identifiers_are_rejected() -> None:
    engine = SignalStreamEngine()

    with pytest.raises(ValueError, match="signal_id"):
        engine.publish(make_event(signal_id=""))

    with pytest.raises(ValueError, match="symbol"):
        engine.publish(make_event(symbol=""))


def test_clear_resets_stream() -> None:
    engine = SignalStreamEngine()

    engine.publish(make_event())

    engine.clear()

    assert engine.sequence == 0
    assert engine.event_count == 0
    assert engine.latest("NIFTY") is None
    assert engine.history() == ()