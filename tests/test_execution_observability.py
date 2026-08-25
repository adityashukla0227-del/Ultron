"""
Tests for Ultron Execution Observability.

v0.45 — Execution Observability
"""

from datetime import datetime, timedelta, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_store import ExecutionEventStore
from modules.agent.execution_observability import (
    ExecutionObservability,
    ExecutionObservabilityError,
)


@pytest.fixture
def store() -> ExecutionEventStore:
    return ExecutionEventStore()


@pytest.fixture
def observability(
    store: ExecutionEventStore,
) -> ExecutionObservability:
    return ExecutionObservability(store)


@pytest.fixture
def events() -> list[ExecutionEvent]:
    return [
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="exec-1",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-1",
            step_id="step-1",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_COMPLETED,
            execution_id="exec-1",
            step_id="step-1",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-1",
            step_id="step-2",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_FAILED,
            execution_id="exec-1",
            step_id="step-2",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
            execution_id="exec-1",
        ),
    ]


# ========================================================
# Query Events
# ========================================================


def test_query_events_returns_all_events_when_no_filters(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.query_events(
        execution_id="exec-1",
    )

    assert result == events


def test_query_events_filters_by_event_type(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.query_events(
        execution_id="exec-1",
        event_type=ExecutionEventType.STEP_FAILED,
    )

    assert len(result) == 1
    assert result[0].event_type == ExecutionEventType.STEP_FAILED
    assert result[0].step_id == "step-2"


def test_query_events_filters_by_step_id(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.query_events(
        execution_id="exec-1",
        step_id="step-1",
    )

    assert len(result) == 2
    assert all(
        event.step_id == "step-1"
        for event in result
    )


def test_query_events_filters_by_event_type_and_step_id(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.query_events(
        execution_id="exec-1",
        event_type=ExecutionEventType.STEP_STARTED,
        step_id="step-2",
    )

    assert len(result) == 1
    assert result[0].event_type == ExecutionEventType.STEP_STARTED
    assert result[0].step_id == "step-2"


def test_query_events_returns_empty_for_unknown_execution(
    observability: ExecutionObservability,
) -> None:
    result = observability.query_events(
        execution_id="unknown",
    )

    assert result == []


def test_query_events_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.query_events(
            execution_id="",
        )


def test_query_events_rejects_invalid_event_type(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.query_events(
            execution_id="exec-1",
            event_type="step_failed",
        )


def test_query_events_rejects_invalid_step_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.query_events(
            execution_id="exec-1",
            step_id="",
        )


# ========================================================
# Existing Observability APIs
# ========================================================


def test_get_events_returns_all_events(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.get_events(
        execution_id="exec-1",
    )

    assert result == events


def test_get_latest_event_returns_latest_event(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.get_latest_event(
        execution_id="exec-1",
    )

    assert result == events[-1]


def test_get_event_count_returns_event_count(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.get_event_count(
        execution_id="exec-1",
    )

    assert result == len(events)


def test_get_step_events_returns_step_events(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = observability.get_step_events(
        execution_id="exec-1",
        step_id="step-1",
    )

    assert len(result) == 2
    assert all(
        event.step_id == "step-1"
        for event in result
    )


def test_get_latest_event_returns_none_for_unknown_execution(
    observability: ExecutionObservability,
) -> None:
    result = observability.get_latest_event(
        execution_id="unknown",
    )

    assert result is None


def test_get_event_count_returns_zero_for_unknown_execution(
    observability: ExecutionObservability,
) -> None:
    result = observability.get_event_count(
        execution_id="unknown",
    )

    assert result == 0


def test_get_step_events_returns_empty_for_unknown_execution(
    observability: ExecutionObservability,
) -> None:
    result = observability.get_step_events(
        execution_id="unknown",
        step_id="step-1",
    )

    assert result == []


def test_get_events_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_events(
            execution_id="",
        )


def test_get_latest_event_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_latest_event(
            execution_id="",
        )


def test_get_event_count_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_event_count(
            execution_id="",
        )


def test_get_step_events_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_step_events(
            execution_id="",
            step_id="step-1",
        )


def test_get_step_events_rejects_invalid_step_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_step_events(
            execution_id="exec-1",
            step_id="",
        )


# ========================================================
# Timeline
# ========================================================


def test_get_timeline_returns_events_in_chronological_order(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
) -> None:
    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    latest = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
        execution_id="exec-1",
        timestamp=base_time + timedelta(seconds=30),
    )

    earliest = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-1",
        timestamp=base_time,
    )

    middle = ExecutionEvent(
        event_type=ExecutionEventType.STEP_STARTED,
        execution_id="exec-1",
        step_id="step-1",
        timestamp=base_time + timedelta(seconds=10),
    )

    store.record_many(
        [
            latest,
            middle,
            earliest,
        ]
    )

    result = observability.get_timeline(
        execution_id="exec-1",
    )

    assert result == [
        earliest,
        middle,
        latest,
    ]


def test_get_timeline_returns_empty_for_unknown_execution(
    observability: ExecutionObservability,
) -> None:
    result = observability.get_timeline(
        execution_id="unknown",
    )

    assert result == []


def test_get_timeline_rejects_invalid_execution_id(
    observability: ExecutionObservability,
) -> None:
    with pytest.raises(ExecutionObservabilityError):
        observability.get_timeline(
            execution_id="",
        )


def test_get_timeline_does_not_modify_store_order(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
) -> None:
    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first_recorded = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
        execution_id="exec-1",
        timestamp=base_time + timedelta(seconds=20),
    )

    second_recorded = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-1",
        timestamp=base_time,
    )

    store.record_many(
        [
            first_recorded,
            second_recorded,
        ]
    )

    original = store.get_events(
        execution_id="exec-1",
    )

    timeline = observability.get_timeline(
        execution_id="exec-1",
    )

    after = store.get_events(
        execution_id="exec-1",
    )

    assert timeline == [
        second_recorded,
        first_recorded,
    ]

    assert after == original


def test_get_timeline_preserves_stable_order_for_equal_timestamps(
    store: ExecutionEventStore,
    observability: ExecutionObservability,
) -> None:
    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first = ExecutionEvent(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        execution_id="exec-1",
        timestamp=timestamp,
    )

    second = ExecutionEvent(
        event_type=ExecutionEventType.STEP_STARTED,
        execution_id="exec-1",
        step_id="step-1",
        timestamp=timestamp,
    )

    third = ExecutionEvent(
        event_type=ExecutionEventType.STEP_COMPLETED,
        execution_id="exec-1",
        step_id="step-1",
        timestamp=timestamp,
    )

    store.record_many(
        [
            first,
            second,
            third,
        ]
    )

    result = observability.get_timeline(
        execution_id="exec-1",
    )

    assert result == [
        first,
        second,
        third,
    ]
