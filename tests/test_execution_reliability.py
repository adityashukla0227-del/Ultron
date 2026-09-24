"""
Ultron Execution Reliability Tests.

v0.86 — Reliability Foundation

Tests the execution reliability validation contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from modules.agent.execution_reliability import (
    ExecutionReliabilityResult,
    ExecutionReliabilityValidator,
)
from modules.agent.execution_state_snapshot import (
    ExecutionStateSnapshot,
)


# ========================================================
# Helpers
# ========================================================


def make_snapshot(
    *,
    execution_id: str = "exec-1",
    status: str = "running",
    current_step_id: str | None = "step-1",
    current_step_index: int | None = 0,
    completed_steps: int = 0,
    failed_steps: int = 0,
    pending_steps: int = 2,
    retry_count: int = 0,
) -> ExecutionStateSnapshot:
    """Create a valid execution state snapshot."""

    return ExecutionStateSnapshot(
        execution_id=execution_id,
        status=status,
        current_step_id=current_step_id,
        current_step_index=current_step_index,
        completed_steps=completed_steps,
        failed_steps=failed_steps,
        pending_steps=pending_steps,
        retry_count=retry_count,
        timestamp=datetime.now(timezone.utc),
    )


# ========================================================
# Result Model
# ========================================================


def test_result_creation():
    """Reliability result should preserve its fields."""

    result = ExecutionReliabilityResult(
        execution_id="exec-1",
        status="running",
        valid=True,
        recoverable=True,
        reason="Execution can be recovered.",
    )

    assert result.execution_id == "exec-1"
    assert result.status == "running"
    assert result.valid is True
    assert result.recoverable is True
    assert result.reason == "Execution can be recovered."


def test_result_is_immutable():
    """Reliability result must be immutable."""

    result = ExecutionReliabilityResult(
        execution_id="exec-1",
        status="running",
        valid=True,
        recoverable=True,
        reason="Execution can be recovered.",
    )

    with pytest.raises(FrozenInstanceError):
        result.valid = False  # type: ignore[misc]


# ========================================================
# Validator
# ========================================================


def test_validator_creation():
    """Validator should be constructible."""

    validator = ExecutionReliabilityValidator()

    assert validator is not None


def test_validator_requires_snapshot():
    """Validator should reject non-snapshot input."""

    validator = ExecutionReliabilityValidator()

    with pytest.raises(TypeError):
        validator.validate(None)  # type: ignore[arg-type]


# ========================================================
# Running
# ========================================================


def test_running_execution_is_recoverable():
    """Running execution should be valid and recoverable."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="running",
            current_step_id="step-1",
            current_step_index=0,
        )
    )

    assert result.valid is True
    assert result.recoverable is True
    assert result.execution_id == "exec-1"
    assert result.status == "running"


# ========================================================
# Paused
# ========================================================


def test_paused_execution_is_recoverable():
    """Paused execution should be valid and recoverable."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="paused",
            current_step_id="step-2",
            current_step_index=1,
        )
    )

    assert result.valid is True
    assert result.recoverable is True
    assert result.status == "paused"


# ========================================================
# Pending
# ========================================================


def test_pending_execution_is_not_recoverable():
    """Pending execution should not be considered recoverable."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="pending",
            current_step_id=None,
            current_step_index=None,
        )
    )

    assert result.valid is True
    assert result.recoverable is False
    assert result.status == "pending"


# ========================================================
# Completed
# ========================================================


def test_completed_execution_is_not_recoverable():
    """Completed execution is terminal."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="completed",
            current_step_id=None,
            current_step_index=None,
            pending_steps=0,
        )
    )

    assert result.valid is True
    assert result.recoverable is False
    assert result.status == "completed"


# ========================================================
# Failed
# ========================================================


def test_failed_execution_is_not_recoverable():
    """Failed execution is terminal under v0.86 semantics."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="failed",
            current_step_id="step-1",
            current_step_index=0,
            failed_steps=1,
        )
    )

    assert result.valid is True
    assert result.recoverable is False
    assert result.status == "failed"


# ========================================================
# Cancelled
# ========================================================


def test_cancelled_execution_is_not_recoverable():
    """Cancelled execution is terminal."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status="cancelled",
            current_step_id=None,
            current_step_index=None,
        )
    )

    assert result.valid is True
    assert result.recoverable is False
    assert result.status == "cancelled"


# ========================================================
# Recovery Consistency
# ========================================================


@pytest.mark.parametrize(
    "status",
    [
        "running",
        "paused",
    ],
)
def test_recoverable_execution_requires_current_step(
    status: str,
):
    """Recoverable execution must preserve its current step."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status=status,
            current_step_id=None,
            current_step_index=None,
        )
    )

    assert result.valid is False
    assert result.recoverable is False
    assert result.status == status
    assert result.reason


@pytest.mark.parametrize(
    "status",
    [
        "completed",
        "cancelled",
    ],
)
def test_terminal_execution_should_not_have_current_step(
    status: str,
):
    """Completed/cancelled execution should not retain a current step."""

    validator = ExecutionReliabilityValidator()

    result = validator.validate(
        make_snapshot(
            status=status,
            current_step_id="step-1",
            current_step_index=0,
        )
    )

    assert result.valid is False
    assert result.recoverable is False
    assert result.status == status
    assert result.reason


# ========================================================
# Determinism
# ========================================================


def test_validation_is_deterministic():
    """Same snapshot should produce equivalent validation results."""

    validator = ExecutionReliabilityValidator()
    snapshot = make_snapshot(
        status="paused",
        current_step_id="step-2",
        current_step_index=1,
    )

    first = validator.validate(snapshot)
    second = validator.validate(snapshot)

    assert first == second


# ========================================================
# Snapshot Independence
# ========================================================


def test_validation_does_not_modify_snapshot():
    """Validation must not mutate the snapshot."""

    validator = ExecutionReliabilityValidator()

    snapshot = make_snapshot(
        status="running",
        current_step_id="step-1",
        current_step_index=0,
    )

    before = snapshot

    validator.validate(snapshot)

    assert snapshot == before