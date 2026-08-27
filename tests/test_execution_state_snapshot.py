"""
Ultron Execution State Snapshot Tests.

v0.48 — Execution State Snapshots

Tests the immutable execution-state snapshot model.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

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
    timestamp: datetime | None = None,
) -> ExecutionStateSnapshot:
    """Create a standard execution state snapshot."""

    return ExecutionStateSnapshot(
        execution_id=execution_id,
        status=status,
        current_step_id=current_step_id,
        current_step_index=current_step_index,
        completed_steps=completed_steps,
        failed_steps=failed_steps,
        pending_steps=pending_steps,
        retry_count=retry_count,
        timestamp=timestamp or datetime.now(timezone.utc),
    )


# ========================================================
# Creation
# ========================================================


def test_snapshot_creation():
    """Snapshot should be created with valid execution state."""

    snapshot = make_snapshot()

    assert snapshot.execution_id == "exec-1"
    assert snapshot.status == "running"
    assert snapshot.current_step_id == "step-1"
    assert snapshot.current_step_index == 0
    assert snapshot.completed_steps == 0
    assert snapshot.failed_steps == 0
    assert snapshot.pending_steps == 2
    assert snapshot.retry_count == 0


def test_snapshot_preserves_timestamp():
    """Snapshot should preserve the provided timestamp."""

    timestamp = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    snapshot = make_snapshot(
        timestamp=timestamp,
    )

    assert snapshot.timestamp == timestamp


# ========================================================
# Execution Identity
# ========================================================


def test_execution_id_must_be_string():
    """execution_id must be a string."""

    with pytest.raises((TypeError, ValueError)):
        make_snapshot(
            execution_id=123,  # type: ignore[arg-type]
        )


def test_execution_id_cannot_be_empty():
    """execution_id cannot be empty."""

    with pytest.raises(ValueError):
        make_snapshot(
            execution_id="",
        )


def test_execution_id_cannot_be_whitespace():
    """execution_id cannot contain only whitespace."""

    with pytest.raises(ValueError):
        make_snapshot(
            execution_id="   ",
        )


# ========================================================
# Status
# ========================================================


@pytest.mark.parametrize(
    "status",
    [
        "pending",
        "running",
        "paused",
        "completed",
        "failed",
        "cancelled",
    ],
)
def test_supported_status_values(status):
    """Supported execution states should be accepted."""

    snapshot = make_snapshot(
        status=status,
    )

    assert snapshot.status == status


def test_status_must_be_string():
    """status must be a string."""

    with pytest.raises((TypeError, ValueError)):
        make_snapshot(
            status=123,  # type: ignore[arg-type]
        )


def test_status_cannot_be_empty():
    """status cannot be empty."""

    with pytest.raises(ValueError):
        make_snapshot(
            status="",
        )


# ========================================================
# Current Step
# ========================================================


def test_current_step_can_be_none():
    """No current step should be supported."""

    snapshot = make_snapshot(
        current_step_id=None,
        current_step_index=None,
    )

    assert snapshot.current_step_id is None
    assert snapshot.current_step_index is None


def test_current_step_id_must_be_string_or_none():
    """current_step_id must be a string or None."""

    with pytest.raises(TypeError):
        make_snapshot(
            current_step_id=123,  # type: ignore[arg-type]
        )


def test_current_step_id_cannot_be_empty():
    """current_step_id cannot be empty."""

    with pytest.raises(ValueError):
        make_snapshot(
            current_step_id="",
        )


def test_current_step_index_cannot_be_negative():
    """current_step_index cannot be negative."""

    with pytest.raises(ValueError):
        make_snapshot(
            current_step_index=-1,
        )


# ========================================================
# Step Counters
# ========================================================


@pytest.mark.parametrize(
    "field_name",
    [
        "completed_steps",
        "failed_steps",
        "pending_steps",
        "retry_count",
    ],
)
def test_step_counters_cannot_be_negative(field_name):
    """Step counters must never be negative."""

    with pytest.raises(ValueError):
        make_snapshot(
            **{field_name: -1},
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "completed_steps",
        "failed_steps",
        "pending_steps",
        "retry_count",
    ],
)
def test_step_counters_must_be_integers(field_name):
    """Step counters must be integers."""

    with pytest.raises(TypeError):
        make_snapshot(
            **{field_name: 1.5},
        )


def test_completed_step_count():
    """Snapshot should preserve completed step count."""

    snapshot = make_snapshot(
        completed_steps=5,
    )

    assert snapshot.completed_steps == 5


def test_failed_step_count():
    """Snapshot should preserve failed step count."""

    snapshot = make_snapshot(
        failed_steps=2,
    )

    assert snapshot.failed_steps == 2


def test_pending_step_count():
    """Snapshot should preserve pending step count."""

    snapshot = make_snapshot(
        pending_steps=7,
    )

    assert snapshot.pending_steps == 7


def test_retry_count():
    """Snapshot should preserve retry count."""

    snapshot = make_snapshot(
        retry_count=3,
    )

    assert snapshot.retry_count == 3


# ========================================================
# Immutability
# ========================================================


def test_snapshot_is_immutable():
    """Execution state snapshots must be immutable."""

    snapshot = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.status = "completed"  # type: ignore[misc]


def test_execution_id_is_immutable():
    """execution_id cannot be modified."""

    snapshot = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.execution_id = "exec-2"  # type: ignore[misc]


def test_current_step_is_immutable():
    """Current step cannot be modified."""

    snapshot = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.current_step_id = "step-2"  # type: ignore[misc]


def test_metrics_are_immutable():
    """Step metrics cannot be modified."""

    snapshot = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.completed_steps = 10  # type: ignore[misc]


# ========================================================
# Serialization
# ========================================================


def test_to_dict():
    """Snapshot should serialize into a dictionary."""

    timestamp = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    snapshot = make_snapshot(
        execution_id="exec-42",
        status="running",
        current_step_id="step-3",
        current_step_index=2,
        completed_steps=2,
        failed_steps=1,
        pending_steps=4,
        retry_count=2,
        timestamp=timestamp,
    )

    data = snapshot.to_dict()

    assert data["execution_id"] == "exec-42"
    assert data["status"] == "running"
    assert data["current_step_id"] == "step-3"
    assert data["current_step_index"] == 2
    assert data["completed_steps"] == 2
    assert data["failed_steps"] == 1
    assert data["pending_steps"] == 4
    assert data["retry_count"] == 2
    assert data["timestamp"] == timestamp.isoformat()


def test_to_dict_returns_new_dictionary():
    """Serialization should return a defensive dictionary."""

    snapshot = make_snapshot()

    first = snapshot.to_dict()
    second = snapshot.to_dict()

    assert first == second
    assert first is not second


# ========================================================
# Deserialization
# ========================================================


def test_from_dict():
    """Snapshot should be reconstructed from serialized data."""

    timestamp = datetime(
        2026,
        8,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )

    data = {
        "execution_id": "exec-100",
        "status": "completed",
        "current_step_id": None,
        "current_step_index": None,
        "completed_steps": 5,
        "failed_steps": 0,
        "pending_steps": 0,
        "retry_count": 1,
        "timestamp": timestamp.isoformat(),
    }

    snapshot = ExecutionStateSnapshot.from_dict(data)

    assert snapshot.execution_id == "exec-100"
    assert snapshot.status == "completed"
    assert snapshot.current_step_id is None
    assert snapshot.current_step_index is None
    assert snapshot.completed_steps == 5
    assert snapshot.failed_steps == 0
    assert snapshot.pending_steps == 0
    assert snapshot.retry_count == 1
    assert snapshot.timestamp == timestamp


def test_from_dict_round_trip():
    """Serialization and deserialization should preserve snapshot data."""

    original = make_snapshot(
        execution_id="exec-round-trip",
        status="paused",
        current_step_id="step-4",
        current_step_index=3,
        completed_steps=3,
        failed_steps=1,
        pending_steps=2,
        retry_count=4,
    )

    restored = ExecutionStateSnapshot.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_from_dict_requires_dictionary():
    """from_dict should reject non-dictionary input."""

    with pytest.raises(TypeError):
        ExecutionStateSnapshot.from_dict(
            None,  # type: ignore[arg-type]
        )


def test_from_dict_missing_execution_id():
    """execution_id is required during deserialization."""

    data = make_snapshot().to_dict()
    data.pop("execution_id")

    with pytest.raises((KeyError, TypeError, ValueError)):
        ExecutionStateSnapshot.from_dict(data)


# ========================================================
# Snapshot Independence
# ========================================================


def test_snapshot_is_independent_value():
    """Snapshot should behave as an independent value object."""

    snapshot = make_snapshot(
        completed_steps=3,
    )

    serialized = snapshot.to_dict()
    serialized["completed_steps"] = 99

    assert snapshot.completed_steps == 3


def test_snapshot_equality():
    """Equivalent snapshots should compare equal."""

    timestamp = datetime(
        2026,
        8,
        27,
        13,
        0,
        tzinfo=timezone.utc,
    )

    first = make_snapshot(
        timestamp=timestamp,
    )

    second = make_snapshot(
        timestamp=timestamp,
    )

    assert first == second


# ========================================================
# Lifecycle Snapshots
# ========================================================


def test_running_snapshot():
    """Running execution should expose its active step."""

    snapshot = make_snapshot(
        status="running",
        current_step_id="step-2",
        current_step_index=1,
    )

    assert snapshot.status == "running"
    assert snapshot.current_step_id == "step-2"
    assert snapshot.current_step_index == 1


def test_paused_snapshot():
    """Paused execution should preserve current execution position."""

    snapshot = make_snapshot(
        status="paused",
        current_step_id="step-2",
        current_step_index=1,
    )

    assert snapshot.status == "paused"
    assert snapshot.current_step_id == "step-2"


def test_completed_snapshot():
    """Completed execution should support no current step."""

    snapshot = make_snapshot(
        status="completed",
        current_step_id=None,
        current_step_index=None,
        completed_steps=5,
        pending_steps=0,
    )

    assert snapshot.status == "completed"
    assert snapshot.current_step_id is None
    assert snapshot.pending_steps == 0


def test_failed_snapshot():
    """Failed execution should preserve failure metrics."""

    snapshot = make_snapshot(
        status="failed",
        failed_steps=1,
        retry_count=2,
    )

    assert snapshot.status == "failed"
    assert snapshot.failed_steps == 1
    assert snapshot.retry_count == 2


def test_cancelled_snapshot():
    """Cancelled execution should preserve its final state."""

    snapshot = make_snapshot(
        status="cancelled",
        current_step_id=None,
        current_step_index=None,
    )

    assert snapshot.status == "cancelled"


# ========================================================
# Public API
# ========================================================


def test_snapshot_has_expected_public_fields():
    """Snapshot should expose the expected state fields."""

    snapshot = make_snapshot()

    assert hasattr(snapshot, "execution_id")
    assert hasattr(snapshot, "status")
    assert hasattr(snapshot, "current_step_id")
    assert hasattr(snapshot, "current_step_index")
    assert hasattr(snapshot, "completed_steps")
    assert hasattr(snapshot, "failed_steps")
    assert hasattr(snapshot, "pending_steps")
    assert hasattr(snapshot, "retry_count")
    assert hasattr(snapshot, "timestamp")


# ========================================================
# Test Completion
# ========================================================


def test_snapshot_model_is_frozen_dataclass():
    """Snapshot should be implemented as a frozen dataclass."""

    snapshot = make_snapshot()

    assert getattr(
        snapshot,
        "__dataclass_fields__",
        None,
    )

    assert getattr(
        snapshot,
        "__dataclass_params__",
        None,
    ).frozen is True