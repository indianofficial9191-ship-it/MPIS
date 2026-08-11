from mpis.live.execution import (
    ExecutionInput,
    ExecutionStatus,
    LiveExecutionGuard,
)


def test_empty_inputs_block():
    result = LiveExecutionGuard().evaluate([])

    assert result.status == ExecutionStatus.BLOCKED
    assert result.execution_score == 0.0


def test_clean_signal_allows_execution():
    inputs = [
        ExecutionInput("decision", True, 0.90, 0.20),
        ExecutionInput("readiness", True, 0.85, 0.10),
    ]

    result = LiveExecutionGuard().evaluate(inputs)

    assert result.status == ExecutionStatus.ALLOWED
    assert result.execution_score > 0.65


def test_not_ready_blocks():
    inputs = [
        ExecutionInput("decision", False, 0.90, 0.10),
    ]

    result = LiveExecutionGuard().evaluate(inputs)

    assert result.status == ExecutionStatus.BLOCKED
    assert "decision:not_ready" in result.reasons


def test_low_confidence_blocks():
    inputs = [
        ExecutionInput("decision", True, 0.50, 0.10),
    ]

    result = LiveExecutionGuard().evaluate(inputs)

    assert result.status == ExecutionStatus.BLOCKED
    assert "decision:low_confidence" in result.reasons


def test_high_risk_blocks():
    inputs = [
        ExecutionInput("decision", True, 0.90, 0.80),
    ]

    result = LiveExecutionGuard().evaluate(inputs)

    assert result.status == ExecutionStatus.BLOCKED
    assert "decision:high_risk" in result.reasons


def test_trap_warning_blocks():
    inputs = [
        ExecutionInput("decision", True, 0.95, 0.10, trap_warning=True),
    ]

    result = LiveExecutionGuard().evaluate(inputs)

    assert result.status == ExecutionStatus.BLOCKED
    assert "decision:trap_warning" in result.reasons
