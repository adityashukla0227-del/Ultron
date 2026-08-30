"""
Tests for the Ultron Agent Execution Event Model.

v0.44 — Agent Execution Observability
"""

from datetime import datetime, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)


# ============================================================
# Creation
# ============================================================


def test_execution_event_creation():
    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-001",
    )

    assert event.event_type == ExecutionEventType.EXECUTION_STARTED
    assert event.execution_id == "exec-001"
    assert event.timestamp.tzinfo is not None


def test_execution_event_default_timestamp_is_utc():
    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-001",
    )

    assert event.timestamp.tzinfo == timezone.utc


def test_execution_event_with_step_information():
    event = ExecutionEvent(
        event_type=ExecutionEventType.STEP_STARTED,
        execution_id="exec-001",
        step_id="step-001",
        step_index=0,
        message="Step started",
    )

    assert event.step_id == "step-001"
    assert event.step_index == 0
    assert event.message == "Step started"


def test_execution_event_metadata():
    event = ExecutionEvent(
        event_type=ExecutionEventType.STEP_COMPLETED,
        execution_id="exec-001",
        metadata={
            "result": "success",
            "duration": 1.25,
        },
    )

    assert event.metadata["result"] == "success"
    assert event.metadata["duration"] == 1.25


def test_execution_event_accepts_string_event_type():
    event = ExecutionEvent(
        event_type="execution_started",
        execution_id="exec-001",
    )

    assert event.event_type == "execution_started"


# ============================================================
# Event Classification
# ============================================================


def test_execution_event_identifies_execution_events():
    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_PAUSED,
        execution_id="exec-001",
    )

    assert event.is_execution_event is True
    assert event.is_step_event is False


def test_execution_event_identifies_step_events():
    event = ExecutionEvent(
        event_type=ExecutionEventType.STEP_FAILED,
        execution_id="exec-001",
        step_id="step-001",
    )

    assert event.is_step_event is True
    assert event.is_execution_event is False


@pytest.mark.parametrize(
    "event_type",
    [
        ExecutionEventType.EXECUTION_STARTED,
        ExecutionEventType.EXECUTION_COMPLETED,
        ExecutionEventType.EXECUTION_FAILED,
        ExecutionEventType.EXECUTION_PAUSED,
        ExecutionEventType.EXECUTION_RESUMED,
        ExecutionEventType.EXECUTION_CANCELLED,
    ],
)
def test_execution_event_lifecycle_types(event_type):
    event = ExecutionEvent(
        event_type=event_type,
        execution_id="exec-001",
    )

    assert event.is_execution_event is True
    assert event.is_step_event is False


@pytest.mark.parametrize(
    "event_type",
    [
        ExecutionEventType.STEP_STARTED,
        ExecutionEventType.STEP_COMPLETED,
        ExecutionEventType.STEP_FAILED,
        ExecutionEventType.STEP_RETRIED,
        ExecutionEventType.STEP_SKIPPED,
    ],
)
def test_step_event_lifecycle_types(event_type):
    event = ExecutionEvent(
        event_type=event_type,
        execution_id="exec-001",
        step_id="step-001",
    )

    assert event.is_step_event is True
    assert event.is_execution_event is False


# ============================================================
# Serialization
# ============================================================


def test_execution_event_to_dict():
    timestamp = datetime(
        2026,
        8,
        23,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    event = ExecutionEvent(
        event_type=ExecutionEventType.STEP_COMPLETED,
        execution_id="exec-001",
        timestamp=timestamp,
        step_id="step-001",
        step_index=2,
        message="Completed successfully",
        metadata={"status": "success"},
    )

    data = event.to_dict()

    assert data == {
        "event_type": "step_completed",
        "execution_id": "exec-001",
        "timestamp": "2026-08-23T10:00:00+00:00",
        "step_id": "step-001",
        "step_index": 2,
        "message": "Completed successfully",
        "metadata": {"status": "success"},
    }


def test_execution_event_from_dict():
    data = {
        "event_type": "step_failed",
        "execution_id": "exec-001",
        "timestamp": "2026-08-23T10:00:00+00:00",
        "step_id": "step-001",
        "step_index": 1,
        "message": "Step failed",
        "metadata": {"error": "timeout"},
    }

    event = ExecutionEvent.from_dict(data)

    assert event.event_type == ExecutionEventType.STEP_FAILED
    assert event.execution_id == "exec-001"
    assert event.step_id == "step-001"
    assert event.step_index == 1
    assert event.message == "Step failed"
    assert event.metadata == {"error": "timeout"}


def test_execution_event_round_trip():
    original = ExecutionEvent(
        event_type=ExecutionEventType.STEP_RETRIED,
        execution_id="exec-001",
        step_id="step-002",
        step_index=2,
        message="Retrying step",
        metadata={"retry_count": 1},
    )

    restored = ExecutionEvent.from_dict(
        original.to_dict()
    )

    assert restored.event_type == original.event_type
    assert restored.execution_id == original.execution_id
    assert restored.step_id == original.step_id
    assert restored.step_index == original.step_index
    assert restored.message == original.message
    assert restored.metadata == original.metadata
    assert restored.timestamp == original.timestamp


def test_execution_event_from_dict_without_timestamp():
    event = ExecutionEvent.from_dict(
        {
            "event_type": "execution_started",
            "execution_id": "exec-001",
        }
    )

    assert event.event_type == ExecutionEventType.EXECUTION_STARTED
    assert event.execution_id == "exec-001"
    assert event.timestamp.tzinfo is not None


def test_execution_event_from_dict_accepts_enum():
    event = ExecutionEvent.from_dict(
        {
            "event_type": ExecutionEventType.EXECUTION_COMPLETED,
            "execution_id": "exec-001",
        }
    )

    assert event.event_type == ExecutionEventType.EXECUTION_COMPLETED


# ============================================================
# Validation
# ============================================================


def test_execution_event_rejects_empty_execution_id():
    with pytest.raises(ValueError):
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="",
        )


def test_execution_event_rejects_whitespace_execution_id():
    with pytest.raises(ValueError):
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="   ",
        )


def test_execution_event_rejects_invalid_execution_id_type():
    with pytest.raises(TypeError):
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id=123,
        )


def test_execution_event_rejects_negative_step_index():
    with pytest.raises(ValueError):
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-001",
            step_index=-1,
        )


def test_execution_event_rejects_invalid_step_id_type():
    with pytest.raises(TypeError):
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-001",
            step_id=123,
        )


def test_execution_event_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="exec-001",
            metadata=["invalid"],
        )


def test_execution_event_rejects_invalid_event_type():
    with pytest.raises(ValueError):
        ExecutionEvent.from_dict(
            {
                "event_type": "invalid_event",
                "execution_id": "exec-001",
            }
        )


def test_execution_event_rejects_invalid_from_dict_input():
    with pytest.raises(TypeError):
        ExecutionEvent.from_dict("invalid")


def test_execution_event_rejects_missing_execution_id():
    with pytest.raises(KeyError):
        ExecutionEvent.from_dict(
            {
                "event_type": "execution_started",
            }
        )


# ============================================================
# Immutability
# ============================================================


def test_execution_event_is_immutable():
    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-001",
    )

    with pytest.raises(AttributeError):
        event.execution_id = "exec-002"


# ============================================================
# Serialization Safety
# ============================================================


def test_execution_event_metadata_is_copied_on_serialization():
    metadata = {"status": "success"}

    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
        execution_id="exec-001",
        metadata=metadata,
    )

    serialized = event.to_dict()

    serialized["metadata"]["status"] = "changed"

    assert event.metadata["status"] == "success"


def test_execution_event_to_dict_returns_metadata_copy():
    metadata = {
        "status": "success",
        "nested": {"value": 1},
    }

    event = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
        execution_id="exec-001",
        metadata=metadata,
    )

    serialized = event.to_dict()

    assert serialized["metadata"] is not event.metadata
    assert serialized["metadata"] == metadata


# ============================================================
# Enum
# ============================================================


def test_execution_event_enum_values():
    assert (
        ExecutionEventType.EXECUTION_STARTED.value
        == "execution_started"
    )
    assert (
        ExecutionEventType.EXECUTION_COMPLETED.value
        == "execution_completed"
    )
    assert (
        ExecutionEventType.EXECUTION_FAILED.value
        == "execution_failed"
    )
    assert (
        ExecutionEventType.EXECUTION_PAUSED.value
        == "execution_paused"
    )
    assert (
        ExecutionEventType.EXECUTION_RESUMED.value
        == "execution_resumed"
    )
    assert (
        ExecutionEventType.EXECUTION_CANCELLED.value
        == "execution_cancelled"
    )

    assert (
        ExecutionEventType.STEP_STARTED.value
        == "step_started"
    )
    assert (
        ExecutionEventType.STEP_COMPLETED.value
        == "step_completed"
    )
    assert (
        ExecutionEventType.STEP_FAILED.value
        == "step_failed"
    )
    assert (
        ExecutionEventType.STEP_RETRIED.value
        == "step_retried"
    )
    assert (
        ExecutionEventType.STEP_SKIPPED.value
        == "step_skipped"
    )