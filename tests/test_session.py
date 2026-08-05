from datetime import datetime, timedelta

from mpis.psychology.session import SessionAnalyzer, SessionType


def test_session_detects_pre_open() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer.get_session(datetime(2026, 8, 3, 9, 5))

    assert result.current_session == SessionType.PRE_OPEN
    assert result.remaining_session_time == timedelta(minutes=10)


def test_session_detects_morning() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer.get_session(datetime(2026, 8, 3, 11, 0))

    assert result.current_session == SessionType.MORNING
    assert result.remaining_session_time == timedelta(hours=1)


def test_session_detects_lunch_session() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer.get_session(datetime(2026, 8, 3, 13, 45))

    assert result.current_session == SessionType.LUNCH
    assert result.remaining_session_time == timedelta(minutes=30)


def test_session_detects_closing_session_with_zero_remaining_after_close() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer.get_session(datetime(2026, 8, 3, 15, 30))

    assert result.current_session == SessionType.CLOSED
    assert result.remaining_session_time == timedelta(0)


def test_session_detects_power_hour() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer.get_session(datetime(2026, 8, 3, 14, 30))

    assert result.current_session == SessionType.POWER_HOUR
    assert result.remaining_session_time == timedelta(minutes=30)
