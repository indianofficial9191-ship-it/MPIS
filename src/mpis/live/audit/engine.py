"""Sprint 22 live decision audit ledger."""

from .models import AuditEvent


class LiveDecisionAuditLedger:
    """In-memory append-only ledger for live decision audit events."""

    def __init__(self) -> None:
        self._events: dict[int, AuditEvent] = {}
        self._next_id = 1

    def record(self, event: AuditEvent) -> int:
        event_id = self._next_id
        self._events[event_id] = event
        self._next_id += 1
        return event_id

    def get(self, event_id: int) -> AuditEvent | None:
        return self._events.get(event_id)

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events.values())

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()
        self._next_id = 1
