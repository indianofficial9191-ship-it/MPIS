import csv
from datetime import datetime
from pathlib import Path

import pytest

from mpis.core.exceptions import ReplayError
from mpis.data import CSVLoader, ReplayBuffer
from mpis.replay import (
    ReplayCallbackRegistry,
    ReplayEngine,
    ReplayFinishedEvent,
    ReplayPausedEvent,
    ReplayResumedEvent,
    ReplaySeekEvent,
    ReplayStartedEvent,
    ReplayStepEvent,
    ReplayRunner,
    ReplaySpeed,
    ReplayStatus,
)
from mpis.replay.models import ReplaySpeed as SpeedEnum
from mpis.replay.state import ReplayState
from mpis.replay.session import ReplaySession


def create_test_buffer(tmp_path: Path) -> ReplayBuffer:
    csv_path = tmp_path / "replay.csv"
    rows = [
        ("2026-07-31", "12:00:00", 100.0, 105.0, 95.0, 102.0),
        ("2026-07-31", "12:01:00", 102.0, 108.0, 101.0, 107.0),
        ("2026-07-31", "12:02:00", 107.0, 109.0, 106.0, 108.0),
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "time", "open", "high", "low", "close"])
        writer.writerows(rows)

    loader = CSVLoader()
    return loader.load(csv_path, "TEST", "1m")


def test_replay_engine_start_pause_resume_stop(tmp_path: Path) -> None:
    buffer = create_test_buffer(tmp_path)
    session = ReplaySession("sess-1", "market", "TEST", "1m", str(tmp_path), datetime.utcnow())
    engine = ReplayEngine(session, buffer, session.clock)
    engine.initialize()

    engine.start()
    assert session.status == ReplayStatus.RUNNING

    engine.pause()
    assert session.status == ReplayStatus.PAUSED

    engine.resume()
    assert session.status == ReplayStatus.RUNNING

    engine.stop()
    assert session.status == ReplayStatus.STOPPED


def test_replay_runner_run_until_index(tmp_path: Path) -> None:
    buffer = create_test_buffer(tmp_path)
    session = ReplaySession("sess-2", "market", "TEST", "1m", str(tmp_path), datetime.utcnow())
    engine = ReplayEngine(session, buffer, session.clock)
    engine.initialize()
    engine.start()

    runner = ReplayRunner(engine)
    runner.run_until(index=1)

    assert engine.current_index() == 1


def test_callback_dispatch_order(tmp_path: Path) -> None:
    buffer = create_test_buffer(tmp_path)
    session = ReplaySession("sess-3", "market", "TEST", "1m", str(tmp_path), datetime.utcnow())
    engine = ReplayEngine(session, buffer, session.clock)
    engine.initialize()
    engine.start()

    events: list[str] = []

    def callback(event):
        events.append(type(event).__name__)

    engine.callbacks.register(callback)
    engine.step()

    assert events == ["ReplayStepEvent"]


def test_replay_engine_invalid_transition() -> None:
    buffer = ReplayBuffer([])
    session = ReplaySession("sess-4", "market", "TEST", "1m", "", datetime.utcnow())
    engine = ReplayEngine(session, buffer, session.clock)
    engine.initialize()

    with pytest.raises(ReplayError):
        engine.pause()
