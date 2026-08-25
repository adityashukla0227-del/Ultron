"""
Tests for Ultron Execution Metrics.

v0.46 — Execution Metrics
"""

from datetime import datetime, timedelta, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_store import ExecutionEventStore
from modules.agent.execution_metrics import (
    ExecutionMetrics,
    ExecutionMetricsCollector,
    ExecutionMetricsError,
)
from modules.agent.execution_observability import (
    ExecutionObservability,
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
def collector(
    observability: ExecutionObservability,
) -> ExecutionMetricsCollector:
    return ExecutionMetricsCollector(observability)


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
            event_type=ExecutionEventType.STEP_RETRIED,
            execution_id="exec-1",
            step_id="step-2",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_COMPLETED,
            execution_id="exec-1",
            step_id="step-2",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-1",
            step_id="step-3",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_FAILED,
            execution_id="exec-1",
            step_id="step-3",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-1",
            step_id="step-4",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_SKIPPED,
            execution_id="exec-1",
            step_id="step-4",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
            execution_id="exec-1",
        ),
    ]


# ========================================================
# Initialization
# ========================================================


def test_collector_accepts_execution_observability(
    observability: ExecutionObservability,
) -> None:
    collector = ExecutionMetricsCollector(
        observability
    )

    assert collector.observability is observability


def test_collector_rejects_invalid_observability() -> None:
    with pytest.raises(ExecutionMetricsError):
        ExecutionMetricsCollector(
            object()  # type: ignore[arg-type]
        )


# ========================================================
# Basic Metrics
# ========================================================


def test_collect_returns_total_event_count(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert isinstance(
        result,
        ExecutionMetrics,
    )

    assert result.execution_id == "exec-1"
    assert result.total_events == len(events)


def test_collect_counts_unique_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.total_steps == 4


def test_collect_counts_completed_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.completed_steps == 2


def test_collect_counts_failed_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.failed_steps == 1


def test_collect_counts_retried_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.retried_steps == 1


def test_collect_counts_skipped_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.skipped_steps == 1


# ========================================================
# Execution Lifecycle Metrics
# ========================================================


def test_collect_detects_execution_completed(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.execution_completed is True


def test_collect_detects_execution_failed(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record(
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_FAILED,
            execution_id="exec-1",
        )
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.execution_failed is True


def test_collect_detects_execution_cancelled(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record(
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_CANCELLED,
            execution_id="exec-1",
        )
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.execution_cancelled is True


def test_collect_detects_execution_paused(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record(
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_PAUSED,
            execution_id="exec-1",
        )
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.execution_paused is True


def test_collect_detects_execution_resumed(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record(
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_RESUMED,
            execution_id="exec-1",
        )
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.execution_resumed is True


# ========================================================
# Unknown Execution
# ========================================================


def test_collect_returns_zero_metrics_for_unknown_execution(
    collector: ExecutionMetricsCollector,
) -> None:
    result = collector.collect(
        execution_id="unknown",
    )

    assert result.execution_id == "unknown"

    assert result.total_events == 0
    assert result.total_steps == 0
    assert result.completed_steps == 0
    assert result.failed_steps == 0
    assert result.retried_steps == 0
    assert result.skipped_steps == 0

    assert result.execution_completed is False
    assert result.execution_failed is False
    assert result.execution_cancelled is False
    assert result.execution_paused is False
    assert result.execution_resumed is False


# ========================================================
# Validation
# ========================================================


def test_collect_rejects_empty_execution_id(
    collector: ExecutionMetricsCollector,
) -> None:
    with pytest.raises(ExecutionMetricsError):
        collector.collect(
            execution_id="",
        )


def test_collect_rejects_whitespace_execution_id(
    collector: ExecutionMetricsCollector,
) -> None:
    with pytest.raises(ExecutionMetricsError):
        collector.collect(
            execution_id="   ",
        )


def test_collect_rejects_non_string_execution_id(
    collector: ExecutionMetricsCollector,
) -> None:
    with pytest.raises(ExecutionMetricsError):
        collector.collect(
            execution_id=123,  # type: ignore[arg-type]
        )


# ========================================================
# Store Isolation
# ========================================================


def test_collect_only_counts_requested_execution(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    other_execution_events = [
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="exec-2",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-2",
            step_id="other-step",
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_COMPLETED,
            execution_id="exec-2",
            step_id="other-step",
        ),
    ]

    store.record_many(
        other_execution_events
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.total_events == len(events)
    assert result.total_steps == 4


# ========================================================
# Read-Only Behavior
# ========================================================


def test_collect_does_not_modify_event_store(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    before = store.get_events(
        execution_id="exec-1",
    )

    collector.collect(
        execution_id="exec-1",
    )

    after = store.get_events(
        execution_id="exec-1",
    )

    assert after == before


# ========================================================
# Record Order Independence
# ========================================================


def test_collect_is_independent_of_event_record_order(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    events = [
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_COMPLETED,
            execution_id="exec-1",
            step_id="step-1",
            timestamp=base_time + timedelta(
                seconds=20
            ),
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_STARTED,
            execution_id="exec-1",
            timestamp=base_time,
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.STEP_STARTED,
            execution_id="exec-1",
            step_id="step-1",
            timestamp=base_time + timedelta(
                seconds=10
            ),
        ),
        ExecutionEvent(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
            execution_id="exec-1",
            timestamp=base_time + timedelta(
                seconds=30
            ),
        ),
    ]

    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.total_events == 4
    assert result.total_steps == 1
    assert result.completed_steps == 1
    assert result.execution_completed is True


# ========================================================
# Event-Type Accuracy
# ========================================================


def test_collect_does_not_count_execution_events_as_steps(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record_many(
        [
            ExecutionEvent(
                event_type=ExecutionEventType.EXECUTION_STARTED,
                execution_id="exec-1",
            ),
            ExecutionEvent(
                event_type=ExecutionEventType.EXECUTION_COMPLETED,
                execution_id="exec-1",
            ),
        ]
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.total_events == 2
    assert result.total_steps == 0


def test_collect_counts_unique_step_ids(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
) -> None:
    store.record_many(
        [
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
                event_type=ExecutionEventType.STEP_RETRIED,
                execution_id="exec-1",
                step_id="step-1",
            ),
        ]
    )

    result = collector.collect(
        execution_id="exec-1",
    )

    assert result.total_steps == 1
    assert result.completed_steps == 1
    assert result.retried_steps == 1


# ========================================================
# Immutable Metrics Snapshot
# ========================================================


def test_metrics_snapshot_is_immutable(
    store: ExecutionEventStore,
    collector: ExecutionMetricsCollector,
    events: list[ExecutionEvent],
) -> None:
    store.record_many(events)

    result = collector.collect(
        execution_id="exec-1",
    )

    with pytest.raises(
        AttributeError
    ):
        result.total_events = 999  # type: ignore[misc]