"""
Tests for the Ultron Agent Execution Event Emitter.

v0.44 — Agent Execution Observability
"""

from datetime import datetime, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_emitter import (
    ExecutionEventEmitter,
)
from modules.agent.execution_event_store import (
    ExecutionEventStore,
)


# ============================================================
# Helpers
# ============================================================


def test_emitter_starts_with_default_store():
    emitter = ExecutionEventEmitter()

    assert isinstance(
        emitter.store,
        ExecutionEventStore,
    )


def test_emitter_accepts_injected_store():
    store = ExecutionEventStore()

    emitter = ExecutionEventEmitter(
        store=store,
    )

    assert emitter.store is store


def test_emit_creates_and_stores_event():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
    )

    assert isinstance(
        event,
        ExecutionEvent,
    )

    assert event.event_type == (
        ExecutionEventType.EXECUTION_STARTED
    )

    assert event.execution_id == "exec-001"

    assert emitter.get_events(
        "exec-001"
    ) == [event]


def test_emit_returns_stored_event():
    store = ExecutionEventStore()
    emitter = ExecutionEventEmitter(store)

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
    )

    assert store.get_latest(
        "exec-001"
    ) is event


def test_emit_rejects_invalid_event_type():
    emitter = ExecutionEventEmitter()

    with pytest.raises(TypeError):
        emitter.emit(
            "execution_started",
            "exec-001",
        )


def test_emit_accepts_explicit_timestamp():
    emitter = ExecutionEventEmitter()

    timestamp = datetime(
        2026,
        8,
        29,
        12,
        30,
        45,
        tzinfo=timezone.utc,
    )

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
        timestamp=timestamp,
    )

    assert event.timestamp == timestamp


def test_emit_creates_timezone_aware_timestamp():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
    )

    assert event.timestamp.tzinfo is not None


def test_emit_timestamp_is_utc():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
    )

    assert (
        event.timestamp.utcoffset()
        == timezone.utc.utcoffset(event.timestamp)
    )


def test_emit_supports_step_fields():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.STEP_STARTED,
        "exec-001",
        step_id="step-001",
        step_index=0,
    )

    assert event.step_id == "step-001"
    assert event.step_index == 0


def test_emit_supports_message():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
        message="Execution started.",
    )

    assert event.message == "Execution started."


def test_emit_supports_metadata():
    emitter = ExecutionEventEmitter()

    metadata = {
        "plan_id": "plan-001",
        "agent_id": "agent-001",
    }

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
        metadata=metadata,
    )

    assert event.metadata == metadata


def test_emit_copies_metadata():
    emitter = ExecutionEventEmitter()

    metadata = {
        "value": "original",
    }

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
        metadata=metadata,
    )

    metadata["value"] = "changed"

    assert event.metadata["value"] == "original"


def test_emit_without_metadata_creates_empty_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.emit(
        ExecutionEventType.EXECUTION_STARTED,
        "exec-001",
    )

    assert event.metadata == {}


# ============================================================
# Execution Lifecycle
# ============================================================


@pytest.mark.parametrize(
    "method,event_type",
    [
        (
            "execution_started",
            ExecutionEventType.EXECUTION_STARTED,
        ),
        (
            "execution_completed",
            ExecutionEventType.EXECUTION_COMPLETED,
        ),
        (
            "execution_failed",
            ExecutionEventType.EXECUTION_FAILED,
        ),
        (
            "execution_paused",
            ExecutionEventType.EXECUTION_PAUSED,
        ),
        (
            "execution_resumed",
            ExecutionEventType.EXECUTION_RESUMED,
        ),
        (
            "execution_cancelled",
            ExecutionEventType.EXECUTION_CANCELLED,
        ),
    ],
)
def test_execution_lifecycle_methods(
    method,
    event_type,
):
    emitter = ExecutionEventEmitter()

    event = getattr(
        emitter,
        method,
    )(
        "exec-001",
    )

    assert isinstance(
        event,
        ExecutionEvent,
    )

    assert event.event_type == event_type
    assert event.execution_id == "exec-001"


def test_execution_started_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_started(
        "exec-001",
        message="Started.",
        metadata={
            "plan_id": "plan-001",
        },
    )

    assert event.message == "Started."
    assert event.metadata == {
        "plan_id": "plan-001",
    }


def test_execution_completed_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_completed(
        "exec-001",
        message="Completed.",
        metadata={
            "result": "success",
        },
    )

    assert event.message == "Completed."
    assert event.metadata == {
        "result": "success",
    }


def test_execution_failed_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_failed(
        "exec-001",
        message="Something failed.",
        metadata={
            "error": "failure",
        },
    )

    assert event.message == "Something failed."
    assert event.metadata == {
        "error": "failure",
    }


def test_execution_paused_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_paused(
        "exec-001",
        message="Paused.",
        metadata={
            "reason": "user_request",
        },
    )

    assert event.message == "Paused."
    assert event.metadata == {
        "reason": "user_request",
    }


def test_execution_resumed_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_resumed(
        "exec-001",
        message="Resumed.",
        metadata={
            "reason": "user_request",
        },
    )

    assert event.message == "Resumed."
    assert event.metadata == {
        "reason": "user_request",
    }


def test_execution_cancelled_supports_message_and_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.execution_cancelled(
        "exec-001",
        message="Cancelled.",
        metadata={
            "reason": "user_request",
        },
    )

    assert event.message == "Cancelled."
    assert event.metadata == {
        "reason": "user_request",
    }


# ============================================================
# Step Lifecycle
# ============================================================


@pytest.mark.parametrize(
    "method,event_type",
    [
        (
            "step_started",
            ExecutionEventType.STEP_STARTED,
        ),
        (
            "step_completed",
            ExecutionEventType.STEP_COMPLETED,
        ),
        (
            "step_failed",
            ExecutionEventType.STEP_FAILED,
        ),
        (
            "step_retried",
            ExecutionEventType.STEP_RETRIED,
        ),
        (
            "step_skipped",
            ExecutionEventType.STEP_SKIPPED,
        ),
    ],
)
def test_step_lifecycle_methods(
    method,
    event_type,
):
    emitter = ExecutionEventEmitter()

    event = getattr(
        emitter,
        method,
    )(
        "exec-001",
        "step-001",
    )

    assert isinstance(
        event,
        ExecutionEvent,
    )

    assert event.event_type == event_type
    assert event.execution_id == "exec-001"
    assert event.step_id == "step-001"


def test_step_started_supports_index_message_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.step_started(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step started.",
        metadata={
            "tool_name": "calculator",
        },
    )

    assert event.step_index == 0
    assert event.message == "Step started."
    assert event.metadata == {
        "tool_name": "calculator",
    }


def test_step_completed_supports_index_message_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.step_completed(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step completed.",
        metadata={
            "result": "ok",
        },
    )

    assert event.step_index == 0
    assert event.message == "Step completed."
    assert event.metadata == {
        "result": "ok",
    }


def test_step_failed_supports_index_message_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.step_failed(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step failed.",
        metadata={
            "error": "tool failure",
        },
    )

    assert event.step_index == 0
    assert event.message == "Step failed."
    assert event.metadata == {
        "error": "tool failure",
    }


def test_step_retried_supports_index_message_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.step_retried(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step retried.",
        metadata={
            "attempt": 2,
        },
    )

    assert event.step_index == 0
    assert event.message == "Step retried."
    assert event.metadata == {
        "attempt": 2,
    }


def test_step_skipped_supports_index_message_metadata():
    emitter = ExecutionEventEmitter()

    event = emitter.step_skipped(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step skipped.",
        metadata={
            "reason": "not_required",
        },
    )

    assert event.step_index == 0
    assert event.message == "Step skipped."
    assert event.metadata == {
        "reason": "not_required",
    }


# ============================================================
# Event Ordering
# ============================================================


def test_emitter_preserves_event_order():
    emitter = ExecutionEventEmitter()

    first = emitter.execution_started(
        "exec-001",
    )

    second = emitter.step_started(
        "exec-001",
        "step-001",
        step_index=0,
    )

    third = emitter.step_completed(
        "exec-001",
        "step-001",
        step_index=0,
    )

    fourth = emitter.execution_completed(
        "exec-001",
    )

    assert emitter.get_events(
        "exec-001"
    ) == [
        first,
        second,
        third,
        fourth,
    ]


def test_emitter_supports_multiple_executions():
    emitter = ExecutionEventEmitter()

    first = emitter.execution_started(
        "exec-001",
    )

    second = emitter.execution_started(
        "exec-002",
    )

    third = emitter.execution_completed(
        "exec-001",
    )

    assert emitter.get_events(
        "exec-001"
    ) == [
        first,
        third,
    ]

    assert emitter.get_events(
        "exec-002"
    ) == [
        second,
    ]


# ============================================================
# Store Access
# ============================================================


def test_get_events_returns_events():
    emitter = ExecutionEventEmitter()

    first = emitter.execution_started(
        "exec-001",
    )
    second = emitter.execution_completed(
        "exec-001",
    )

    assert emitter.get_events(
        "exec-001"
    ) == [
        first,
        second,
    ]


def test_get_events_returns_empty_for_unknown_execution():
    emitter = ExecutionEventEmitter()

    assert emitter.get_events(
        "missing"
    ) == []


def test_get_latest_returns_latest_event():
    emitter = ExecutionEventEmitter()

    emitter.execution_started(
        "exec-001",
    )

    latest = emitter.execution_completed(
        "exec-001",
    )

    assert emitter.get_latest(
        "exec-001"
    ) is latest


def test_get_latest_returns_none_for_unknown_execution():
    emitter = ExecutionEventEmitter()

    assert emitter.get_latest(
        "missing"
    ) is None


def test_get_step_events_returns_matching_events():
    emitter = ExecutionEventEmitter()

    first = emitter.step_started(
        "exec-001",
        "step-001",
        step_index=0,
    )

    second = emitter.step_started(
        "exec-001",
        "step-002",
        step_index=1,
    )

    third = emitter.step_completed(
        "exec-001",
        "step-001",
        step_index=0,
    )

    assert emitter.get_step_events(
        "exec-001",
        "step-001",
    ) == [
        first,
        third,
    ]

    assert emitter.get_step_events(
        "exec-001",
        "step-002",
    ) == [
        second,
    ]


def test_get_step_events_returns_empty_for_unknown_step():
    emitter = ExecutionEventEmitter()

    emitter.step_started(
        "exec-001",
        "step-001",
    )

    assert emitter.get_step_events(
        "exec-001",
        "missing",
    ) == []


def test_count_returns_event_count():
    emitter = ExecutionEventEmitter()

    assert emitter.count(
        "exec-001"
    ) == 0

    emitter.execution_started(
        "exec-001",
    )

    emitter.step_started(
        "exec-001",
        "step-001",
    )

    emitter.execution_completed(
        "exec-001",
    )

    assert emitter.count(
        "exec-001"
    ) == 3


def test_clear_specific_execution():
    emitter = ExecutionEventEmitter()

    emitter.execution_started(
        "exec-001",
    )

    emitter.execution_started(
        "exec-002",
    )

    emitter.clear(
        "exec-001"
    )

    assert emitter.get_events(
        "exec-001"
    ) == []

    assert emitter.count(
        "exec-002"
    ) == 1


def test_clear_all_events():
    emitter = ExecutionEventEmitter()

    emitter.execution_started(
        "exec-001",
    )

    emitter.execution_started(
        "exec-002",
    )

    emitter.clear()

    assert emitter.get_events(
        "exec-001"
    ) == []

    assert emitter.get_events(
        "exec-002"
    ) == []


# ============================================================
# Validation Delegation
# ============================================================


@pytest.mark.parametrize(
    "method",
    [
        "get_events",
        "get_latest",
        "count",
        "clear",
    ],
)
def test_execution_id_none_validation(
    method,
):
    emitter = ExecutionEventEmitter()

    with pytest.raises(TypeError):
        getattr(
            emitter,
            method,
        )(None)


@pytest.mark.parametrize(
    "method",
    [
        "get_events",
        "get_latest",
        "count",
        "clear",
    ],
)
def test_execution_id_empty_validation(
    method,
):
    emitter = ExecutionEventEmitter()

    with pytest.raises(ValueError):
        getattr(
            emitter,
            method,
        )("")


def test_get_step_events_validates_execution_id():
    emitter = ExecutionEventEmitter()

    with pytest.raises(TypeError):
        emitter.get_step_events(
            None,
            "step-001",
        )


def test_get_step_events_validates_empty_execution_id():
    emitter = ExecutionEventEmitter()

    with pytest.raises(ValueError):
        emitter.get_step_events(
            "",
            "step-001",
        )


def test_get_step_events_validates_step_id_type():
    emitter = ExecutionEventEmitter()

    with pytest.raises(TypeError):
        emitter.get_step_events(
            "exec-001",
            123,
        )


def test_get_step_events_validates_empty_step_id():
    emitter = ExecutionEventEmitter()

    with pytest.raises(ValueError):
        emitter.get_step_events(
            "exec-001",
            "",
        )


# ============================================================
# Representation
# ============================================================


def test_repr_contains_class_name():
    emitter = ExecutionEventEmitter()

    representation = repr(
        emitter
    )

    assert (
        "ExecutionEventEmitter"
        in representation
    )


def test_repr_contains_store():
    store = ExecutionEventStore()

    emitter = ExecutionEventEmitter(
        store=store,
    )

    representation = repr(
        emitter
    )

    assert "store=" in representation


# ============================================================
# Integration
# ============================================================


def test_full_execution_event_sequence():
    emitter = ExecutionEventEmitter()

    started = emitter.execution_started(
        "exec-001",
        message="Execution started.",
        metadata={
            "plan_id": "plan-001",
            "agent_id": "agent-001",
        },
    )

    step_started = emitter.step_started(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step started.",
        metadata={
            "tool_name": "calculator",
        },
    )

    step_completed = emitter.step_completed(
        "exec-001",
        "step-001",
        step_index=0,
        message="Step completed.",
        metadata={
            "result": 42,
        },
    )

    completed = emitter.execution_completed(
        "exec-001",
        message="Execution completed.",
        metadata={
            "result": "success",
        },
    )

    events = emitter.get_events(
        "exec-001"
    )

    assert events == [
        started,
        step_started,
        step_completed,
        completed,
    ]

    assert emitter.get_latest(
        "exec-001"
    ) is completed

    assert emitter.count(
        "exec-001"
    ) == 4

    assert emitter.get_step_events(
        "exec-001",
        "step-001",
    ) == [
        step_started,
        step_completed,
    ]
