import time

import pytest

from mpis.core import Timer


def test_timer_context_manager() -> None:
    with Timer("test") as start:
        time.sleep(0.01)
    elapsed = start
    assert elapsed is not None
    assert elapsed >= 0.0


def test_timer_get_elapsed_after_context() -> None:
    timer = Timer("test")
    with timer:
        time.sleep(0.01)
    assert timer.get_elapsed() >= 0.0


def test_timer_reset() -> None:
    timer = Timer()
    with timer:
        pass
    timer.reset()
    with pytest.raises(RuntimeError):
        timer.get_elapsed()
