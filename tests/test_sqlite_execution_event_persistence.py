"""
Tests for Ultron SQLite Execution Event Persistence.

v0.47 — Persistent Execution History
"""

from datetime import datetime, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_persistence import (
    ExecutionEventPersistenceError,
)
from modules.agent.sqlite_execution_event_persistence import (
    SQLiteExecutionEventPersistence,
)


# ============================================================
# Helpers
# ============================================================


def make_event(
    execution_id: str = "exec-1",
    event_type: ExecutionEventType = ExecutionEventType.EXECUTION_STARTED,
    *,
    step_id: str | None = None,
    step_index: int | None = None,
    message: str | None = None,
    metadata: dict | None = None,
    timestamp: datetime | None = None,
) -> ExecutionEvent:
    """Create a test execution event."""

    return ExecutionEvent(
        event_type=event_type,
        execution_id=execution_id,
        timestamp=timestamp or datetime.now(timezone.utc),
        step_id=step_id,
        step_index=step_index,
        message=message,
        metadata=metadata or {},
    )


@pytest.fixture
def persistence(tmp_path):
    """Provide a temporary SQLite persistence instance."""

    database_path = tmp_path / "execution_events.db"

    store = SQLiteExecutionEventPersistence(
        database_path
    )

    yield store

    store.close()


# ============================================================
# Initialization
# ============================================================


def test_persistence_creates_database(persistence):
    """SQLite persistence should initialize successfully."""

    assert persistence.database_path.exists()


def test_invalid_database_path_type():
    """Invalid database path types should be rejected."""

    with pytest.raises(ExecutionEventPersistenceError):
        SQLiteExecutionEventPersistence(123)


def test_empty_database_path():
    """Empty database paths should be rejected."""

    with pytest.raises(ExecutionEventPersistenceError):
        SQLiteExecutionEventPersistence("")


# ============================================================
# Save
# ============================================================


def test_save_event(persistence):
    """A single execution event should be persisted."""

    event = make_event()

    result = persistence.save(event)

    assert result == event
    assert persistence.count("exec-1") == 1


def test_save_rejects_invalid_event(persistence):
    """save() should reject invalid event objects."""

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.save("invalid")


def test_saved_event_can_be_retrieved(persistence):
    """Persisted events should be retrievable."""

    event = make_event(
        event_type=ExecutionEventType.EXECUTION_STARTED,
        message="Execution started",
    )

    persistence.save(event)

    events = persistence.get_events("exec-1")

    assert len(events) == 1
    assert events[0] == event


# ============================================================
# Save Many
# ============================================================


def test_save_many_events(persistence):
    """Multiple events should be persisted."""

    events = [
        make_event(
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-1",
            step_index=0,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-1",
            step_index=0,
        ),
        make_event(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    result = persistence.save_many(events)

    assert result == events
    assert persistence.count("exec-1") == 4


def test_save_many_rejects_non_list(persistence):
    """save_many() should require a list."""

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.save_many("invalid")


def test_save_many_rejects_invalid_event(persistence):
    """save_many() should reject invalid events."""

    events = [
        make_event(),
        "invalid",
    ]

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.save_many(events)

    assert persistence.count("exec-1") == 0


def test_save_many_is_atomic(persistence):
    """Invalid batch input should not partially persist."""

    events = [
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-1",
        ),
        "invalid",
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-1",
        ),
    ]

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.save_many(events)

    assert persistence.count("exec-1") == 0


# ============================================================
# Retrieval
# ============================================================


def test_get_events_returns_events_in_insertion_order(persistence):
    """Events should preserve insertion order."""

    events = [
        make_event(
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-1",
        ),
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-1",
        ),
        make_event(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    persistence.save_many(events)

    retrieved = persistence.get_events("exec-1")

    assert retrieved == events


def test_get_events_unknown_execution_returns_empty_list(
    persistence,
):
    """Unknown executions should return an empty list."""

    assert persistence.get_events("unknown") == []


def test_get_latest_returns_latest_event(persistence):
    """get_latest() should return the last persisted event."""

    events = [
        make_event(
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    persistence.save_many(events)

    latest = persistence.get_latest("exec-1")

    assert latest == events[-1]


def test_get_latest_unknown_execution_returns_none(
    persistence,
):
    """Unknown executions should return None."""

    assert persistence.get_latest("unknown") is None


# ============================================================
# Counting
# ============================================================


def test_count_returns_event_count(persistence):
    """count() should return the number of persisted events."""

    events = [
        make_event(),
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-1",
        ),
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-1",
        ),
    ]

    persistence.save_many(events)

    assert persistence.count("exec-1") == 3


def test_count_unknown_execution_returns_zero(persistence):
    """Unknown executions should have a count of zero."""

    assert persistence.count("unknown") == 0


# ============================================================
# Execution IDs
# ============================================================


def test_execution_ids_returns_all_execution_ids(
    persistence,
):
    """execution_ids() should return all stored execution IDs."""

    persistence.save(
        make_event(
            execution_id="exec-1",
        )
    )

    persistence.save(
        make_event(
            execution_id="exec-2",
        )
    )

    persistence.save(
        make_event(
            execution_id="exec-3",
        )
    )

    assert persistence.execution_ids() == [
        "exec-1",
        "exec-2",
        "exec-3",
    ]


def test_execution_ids_empty_store(persistence):
    """Empty persistence should return no execution IDs."""

    assert persistence.execution_ids() == []


# ============================================================
# Data Preservation
# ============================================================


def test_metadata_is_preserved(persistence):
    """Event metadata should survive persistence."""

    event = make_event(
        metadata={
            "tool": "web_search",
            "attempt": 2,
            "success": True,
        }
    )

    persistence.save(event)

    retrieved = persistence.get_events("exec-1")[0]

    assert retrieved.metadata == event.metadata


def test_timestamp_is_preserved(persistence):
    """Event timestamps should survive persistence."""

    timestamp = datetime(
        2026,
        8,
        27,
        10,
        30,
        45,
        123456,
        tzinfo=timezone.utc,
    )

    event = make_event(
        timestamp=timestamp,
    )

    persistence.save(event)

    retrieved = persistence.get_events("exec-1")[0]

    assert retrieved.timestamp == timestamp


def test_step_information_is_preserved(persistence):
    """Step ID and step index should survive persistence."""

    event = make_event(
        event_type=ExecutionEventType.STEP_COMPLETED,
        step_id="step-42",
        step_index=41,
    )

    persistence.save(event)

    retrieved = persistence.get_events("exec-1")[0]

    assert retrieved.step_id == "step-42"
    assert retrieved.step_index == 41


def test_message_is_preserved(persistence):
    """Event messages should survive persistence."""

    event = make_event(
        message="Tool execution completed successfully",
    )

    persistence.save(event)

    retrieved = persistence.get_events("exec-1")[0]

    assert retrieved.message == event.message


def test_event_type_is_preserved(persistence):
    """Event types should survive persistence."""

    event = make_event(
        event_type=ExecutionEventType.STEP_RETRIED,
        step_id="step-1",
    )

    persistence.save(event)

    retrieved = persistence.get_events("exec-1")[0]

    assert retrieved.event_type == ExecutionEventType.STEP_RETRIED


# ============================================================
# Multiple Executions
# ============================================================


def test_multiple_executions_are_isolated(persistence):
    """Events from different executions should remain isolated."""

    event_1 = make_event(
        execution_id="exec-1",
    )

    event_2 = make_event(
        execution_id="exec-2",
    )

    persistence.save(event_1)
    persistence.save(event_2)

    assert persistence.get_events("exec-1") == [event_1]
    assert persistence.get_events("exec-2") == [event_2]


def test_count_is_execution_specific(persistence):
    """Event counts should be isolated per execution."""

    persistence.save_many(
        [
            make_event(execution_id="exec-1"),
            make_event(execution_id="exec-1"),
            make_event(execution_id="exec-1"),
        ]
    )

    persistence.save(
        make_event(
            execution_id="exec-2",
        )
    )

    assert persistence.count("exec-1") == 3
    assert persistence.count("exec-2") == 1


# ============================================================
# Validation
# ============================================================


@pytest.mark.parametrize(
    "execution_id",
    [
        "",
        "   ",
        None,
        123,
        [],
    ],
)
def test_get_events_validates_execution_id(
    persistence,
    execution_id,
):
    """get_events() should validate execution IDs."""

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.get_events(execution_id)


@pytest.mark.parametrize(
    "execution_id",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_get_latest_validates_execution_id(
    persistence,
    execution_id,
):
    """get_latest() should validate execution IDs."""

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.get_latest(execution_id)


@pytest.mark.parametrize(
    "execution_id",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_count_validates_execution_id(
    persistence,
    execution_id,
):
    """count() should validate execution IDs."""

    with pytest.raises(ExecutionEventPersistenceError):
        persistence.count(execution_id)


# ============================================================
# Clear
# ============================================================


def test_clear_single_execution(persistence):
    """clear(execution_id) should remove only that execution."""

    event_1 = make_event(
        execution_id="exec-1",
    )

    event_2 = make_event(
        execution_id="exec-2",
    )

    persistence.save(event_1)
    persistence.save(event_2)

    persistence.clear("exec-1")

    assert persistence.get_events("exec-1") == []
    assert persistence.get_events("exec-2") == [event_2]


def test_clear_all_executions(persistence):
    """clear() should remove all persisted events."""

    persistence.save(
        make_event(
            execution_id="exec-1",
        )
    )

    persistence.save(
        make_event(
            execution_id="exec-2",
        )
    )

    persistence.clear()

    assert persistence.execution_ids() == []
    assert persistence.count("exec-1") == 0
    assert persistence.count("exec-2") == 0


def test_clear_unknown_execution_is_safe(persistence):
    """Clearing an unknown execution should be harmless."""

    persistence.clear("unknown")

    assert persistence.execution_ids() == []


# ============================================================
# Persistence Across Connections
# ============================================================


def test_events_persist_across_connections(tmp_path):
    """
    Events should remain available after closing and
    reopening the SQLite connection.
    """

    database_path = tmp_path / "persistent_events.db"

    event = make_event(
        execution_id="persistent-exec",
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
        metadata={"persistent": True},
    )

    first = SQLiteExecutionEventPersistence(
        database_path
    )

    first.save(event)
    first.close()

    second = SQLiteExecutionEventPersistence(
        database_path
    )

    try:
        events = second.get_events(
            "persistent-exec"
        )

        assert events == [event]

    finally:
        second.close()


def test_multiple_events_persist_across_connections(
    tmp_path,
):
    """Multiple events should survive connection reopening."""

    database_path = tmp_path / "persistent_events.db"

    events = [
        make_event(
            execution_id="persistent-exec",
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            execution_id="persistent-exec",
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-1",
        ),
        make_event(
            execution_id="persistent-exec",
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-1",
        ),
        make_event(
            execution_id="persistent-exec",
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    first = SQLiteExecutionEventPersistence(
        database_path
    )

    first.save_many(events)
    first.close()

    second = SQLiteExecutionEventPersistence(
        database_path
    )

    try:
        assert second.get_events(
            "persistent-exec"
        ) == events

        assert second.count(
            "persistent-exec"
        ) == 4

    finally:
        second.close()


# ============================================================
# Context Manager
# ============================================================


def test_context_manager_closes_connection(tmp_path):
    """Persistence should support context-manager usage."""

    database_path = tmp_path / "context.db"

    with SQLiteExecutionEventPersistence(
        database_path
    ) as persistence:
        persistence.save(
            make_event()
        )

    assert database_path.exists()