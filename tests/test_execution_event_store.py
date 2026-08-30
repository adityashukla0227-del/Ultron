"""
Tests for the Ultron Agent Execution Event Store.

v0.44 — Agent Execution Observability
"""

from datetime import datetime, timezone

import pytest

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_store import ExecutionEventStore


def make_event(
    execution_id: str = "exec-001",
    event_type: ExecutionEventType = ExecutionEventType.EXECUTION_STARTED,
    step_id: str | None = None,
    step_index: int | None = None,
) -> ExecutionEvent:
    return ExecutionEvent(
        event_type=event_type,
        execution_id=execution_id,
        timestamp=datetime.now(timezone.utc),
        step_id=step_id,
        step_index=step_index,
    )


# ============================================================
# Initialization
# ============================================================


def test_store_starts_empty():
    store = ExecutionEventStore()

    assert store.execution_ids() == []
    assert store.snapshot() == {}


# ============================================================
# Record
# ============================================================


def test_record_event():
    store = ExecutionEventStore()
    event = make_event()

    result = store.record(event)

    assert result is event
    assert store.get_events("exec-001") == [event]
    assert store.count("exec-001") == 1


def test_record_preserves_insertion_order():
    store = ExecutionEventStore()

    first = make_event(
        event_type=ExecutionEventType.EXECUTION_STARTED,
    )
    second = make_event(
        event_type=ExecutionEventType.STEP_STARTED,
        step_id="step-001",
        step_index=0,
    )
    third = make_event(
        event_type=ExecutionEventType.STEP_COMPLETED,
        step_id="step-001",
        step_index=0,
    )

    store.record(first)
    store.record(second)
    store.record(third)

    assert store.get_events("exec-001") == [
        first,
        second,
        third,
    ]


def test_record_rejects_invalid_event():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.record("invalid")


def test_record_rejects_none():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.record(None)


# ============================================================
# Record Many
# ============================================================


def test_record_many():
    store = ExecutionEventStore()

    events = [
        make_event(
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-001",
            step_index=0,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-001",
            step_index=0,
        ),
    ]

    result = store.record_many(events)

    assert result == events
    assert store.get_events("exec-001") == events
    assert store.count("exec-001") == 3


def test_record_many_preserves_global_insertion_order_per_execution():
    store = ExecutionEventStore()

    first = make_event(
        "exec-001",
        ExecutionEventType.EXECUTION_STARTED,
    )
    second = make_event(
        "exec-002",
        ExecutionEventType.EXECUTION_STARTED,
    )
    third = make_event(
        "exec-001",
        ExecutionEventType.EXECUTION_COMPLETED,
    )
    fourth = make_event(
        "exec-002",
        ExecutionEventType.EXECUTION_COMPLETED,
    )

    store.record_many(
        [
            first,
            second,
            third,
            fourth,
        ]
    )

    assert store.get_events("exec-001") == [
        first,
        third,
    ]

    assert store.get_events("exec-002") == [
        second,
        fourth,
    ]


def test_record_many_supports_multiple_executions():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    second = make_event("exec-002")
    third = make_event("exec-001")

    store.record_many(
        [
            first,
            second,
            third,
        ]
    )

    assert store.get_events("exec-001") == [
        first,
        third,
    ]

    assert store.get_events("exec-002") == [
        second,
    ]


def test_record_many_accepts_empty_list():
    store = ExecutionEventStore()

    result = store.record_many([])

    assert result == []
    assert store.snapshot() == {}


def test_record_many_rejects_non_list():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.record_many("invalid")


def test_record_many_rejects_tuple():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.record_many(
            (
                make_event(),
            )
        )


def test_record_many_rejects_none():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.record_many(None)


def test_record_many_rejects_invalid_event():
    store = ExecutionEventStore()

    valid_event = make_event()

    with pytest.raises(TypeError):
        store.record_many(
            [
                valid_event,
                "invalid",
            ]
        )

    assert store.snapshot() == {}


def test_record_many_validates_all_events_before_recording():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    invalid = "invalid"
    third = make_event("exec-002")

    with pytest.raises(TypeError):
        store.record_many(
            [
                first,
                invalid,
                third,
            ]
        )

    # Atomic validation: no event should have been stored.
    assert store.snapshot() == {}


# ============================================================
# Get Events
# ============================================================


def test_get_events_returns_empty_list_for_unknown_execution():
    store = ExecutionEventStore()

    assert store.get_events("missing") == []


def test_get_events_returns_defensive_copy():
    store = ExecutionEventStore()
    event = make_event()

    store.record(event)

    events = store.get_events("exec-001")

    events.clear()

    assert store.count("exec-001") == 1
    assert store.get_events("exec-001") == [event]


def test_get_events_does_not_expose_internal_list():
    store = ExecutionEventStore()

    first = make_event()
    second = make_event(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
    )

    store.record(first)

    events = store.get_events("exec-001")
    events.append(second)

    assert store.get_events("exec-001") == [first]


# ============================================================
# Latest
# ============================================================


def test_get_latest_returns_latest_event():
    store = ExecutionEventStore()

    first = make_event(
        event_type=ExecutionEventType.EXECUTION_STARTED,
    )
    second = make_event(
        event_type=ExecutionEventType.EXECUTION_COMPLETED,
    )

    store.record(first)
    store.record(second)

    assert store.get_latest("exec-001") is second


def test_get_latest_returns_none_for_unknown_execution():
    store = ExecutionEventStore()

    assert store.get_latest("missing") is None


def test_get_latest_after_multiple_events():
    store = ExecutionEventStore()

    events = [
        make_event(
            event_type=ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-001",
        ),
        make_event(
            event_type=ExecutionEventType.STEP_COMPLETED,
            step_id="step-001",
        ),
        make_event(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    store.record_many(events)

    assert store.get_latest("exec-001") is events[-1]


# ============================================================
# Step Events
# ============================================================


def test_get_step_events():
    store = ExecutionEventStore()

    step_one_started = make_event(
        event_type=ExecutionEventType.STEP_STARTED,
        step_id="step-001",
        step_index=0,
    )

    step_two_started = make_event(
        event_type=ExecutionEventType.STEP_STARTED,
        step_id="step-002",
        step_index=1,
    )

    step_one_completed = make_event(
        event_type=ExecutionEventType.STEP_COMPLETED,
        step_id="step-001",
        step_index=0,
    )

    store.record_many(
        [
            step_one_started,
            step_two_started,
            step_one_completed,
        ]
    )

    assert store.get_step_events(
        "exec-001",
        "step-001",
    ) == [
        step_one_started,
        step_one_completed,
    ]


def test_get_step_events_preserves_order():
    store = ExecutionEventStore()

    events = [
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-001",
        ),
        make_event(
            event_type=ExecutionEventType.STEP_RETRIED,
            step_id="step-001",
        ),
        make_event(
            event_type=ExecutionEventType.STEP_FAILED,
            step_id="step-001",
        ),
    ]

    store.record_many(events)

    assert store.get_step_events(
        "exec-001",
        "step-001",
    ) == events


def test_get_step_events_returns_empty_for_unknown_step():
    store = ExecutionEventStore()

    store.record(
        make_event(
            event_type=ExecutionEventType.STEP_STARTED,
            step_id="step-001",
        )
    )

    assert store.get_step_events(
        "exec-001",
        "missing",
    ) == []


def test_get_step_events_does_not_mix_executions():
    store = ExecutionEventStore()

    first = make_event(
        "exec-001",
        ExecutionEventType.STEP_STARTED,
        "step-001",
    )

    second = make_event(
        "exec-002",
        ExecutionEventType.STEP_STARTED,
        "step-001",
    )

    store.record_many(
        [
            first,
            second,
        ]
    )

    assert store.get_step_events(
        "exec-001",
        "step-001",
    ) == [first]

    assert store.get_step_events(
        "exec-002",
        "step-001",
    ) == [second]


# ============================================================
# Counts / Existence
# ============================================================


def test_count():
    store = ExecutionEventStore()

    assert store.count("exec-001") == 0

    store.record(make_event())

    assert store.count("exec-001") == 1

    store.record(
        make_event(
            event_type=ExecutionEventType.EXECUTION_COMPLETED,
        )
    )

    assert store.count("exec-001") == 2


def test_count_isolated_by_execution():
    store = ExecutionEventStore()

    store.record(make_event("exec-001"))
    store.record(make_event("exec-002"))
    store.record(make_event("exec-001"))

    assert store.count("exec-001") == 2
    assert store.count("exec-002") == 1


def test_has_events():
    store = ExecutionEventStore()

    assert store.has_events("exec-001") is False

    store.record(make_event())

    assert store.has_events("exec-001") is True


def test_has_events_isolated_by_execution():
    store = ExecutionEventStore()

    store.record(make_event("exec-001"))

    assert store.has_events("exec-001") is True
    assert store.has_events("exec-002") is False


# ============================================================
# Execution IDs
# ============================================================


def test_execution_ids():
    store = ExecutionEventStore()

    store.record(make_event("exec-001"))
    store.record(make_event("exec-002"))

    assert store.execution_ids() == [
        "exec-001",
        "exec-002",
    ]


def test_execution_ids_do_not_duplicate():
    store = ExecutionEventStore()

    store.record(make_event("exec-001"))
    store.record(make_event("exec-001"))
    store.record(make_event("exec-002"))

    assert store.execution_ids() == [
        "exec-001",
        "exec-002",
    ]


def test_execution_ids_preserve_first_seen_order():
    store = ExecutionEventStore()

    store.record(make_event("exec-003"))
    store.record(make_event("exec-001"))
    store.record(make_event("exec-002"))
    store.record(make_event("exec-001"))

    assert store.execution_ids() == [
        "exec-003",
        "exec-001",
        "exec-002",
    ]


# ============================================================
# Clear
# ============================================================


def test_clear_specific_execution():
    store = ExecutionEventStore()

    event_one = make_event("exec-001")
    event_two = make_event("exec-002")

    store.record(event_one)
    store.record(event_two)

    store.clear("exec-001")

    assert store.get_events("exec-001") == []
    assert store.get_events("exec-002") == [event_two]


def test_clear_all_executions():
    store = ExecutionEventStore()

    store.record(make_event("exec-001"))
    store.record(make_event("exec-002"))

    store.clear()

    assert store.execution_ids() == []
    assert store.snapshot() == {}


def test_clear_unknown_execution_is_safe():
    store = ExecutionEventStore()

    store.clear("missing")

    assert store.execution_ids() == []


def test_clear_preserves_other_execution_history():
    store = ExecutionEventStore()

    events_one = [
        make_event(
            "exec-001",
            ExecutionEventType.EXECUTION_STARTED,
        ),
        make_event(
            "exec-001",
            ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    events_two = [
        make_event(
            "exec-002",
            ExecutionEventType.EXECUTION_STARTED,
        ),
    ]

    store.record_many(events_one)
    store.record_many(events_two)

    store.clear("exec-001")

    assert store.get_events("exec-001") == []
    assert store.get_events("exec-002") == events_two


def test_store_can_be_reused_after_clear():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    store.record(first)

    store.clear("exec-001")

    second = make_event(
        "exec-001",
        ExecutionEventType.EXECUTION_STARTED,
    )

    store.record(second)

    assert store.get_events("exec-001") == [second]
    assert store.execution_ids() == ["exec-001"]


def test_clear_none_is_invalid():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.clear(None)


# ============================================================
# Snapshot
# ============================================================


def test_snapshot():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    second = make_event("exec-002")

    store.record(first)
    store.record(second)

    snapshot = store.snapshot()

    assert snapshot == {
        "exec-001": [first],
        "exec-002": [second],
    }


def test_snapshot_is_defensive():
    store = ExecutionEventStore()

    event = make_event()

    store.record(event)

    snapshot = store.snapshot()

    snapshot["exec-001"].clear()

    assert store.count("exec-001") == 1
    assert store.get_events("exec-001") == [event]


def test_snapshot_does_not_expose_internal_lists():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    second = make_event("exec-002")

    store.record(first)
    store.record(second)

    snapshot = store.snapshot()

    snapshot["exec-001"].append(second)
    snapshot["exec-002"].clear()

    assert store.get_events("exec-001") == [first]
    assert store.get_events("exec-002") == [second]


def test_snapshot_preserves_execution_order():
    store = ExecutionEventStore()

    first = make_event("exec-001")
    second = make_event("exec-001")
    third = make_event("exec-002")

    store.record(first)
    store.record(second)
    store.record(third)

    snapshot = store.snapshot()

    assert snapshot["exec-001"] == [
        first,
        second,
    ]

    assert snapshot["exec-002"] == [
        third,
    ]


# ============================================================
# Execution ID Validation
# ============================================================


@pytest.mark.parametrize(
    "method,args",
    [
        ("get_events", (None,)),
        ("get_latest", (None,)),
        ("count", (None,)),
        ("has_events", (None,)),
        ("clear", (None,)),
    ],
)
def test_execution_id_validation(method, args):
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        getattr(store, method)(*args)


@pytest.mark.parametrize(
    "method,args",
    [
        ("get_events", ("",)),
        ("get_latest", ("",)),
        ("count", ("",)),
        ("has_events", ("",)),
        ("clear", ("",)),
    ],
)
def test_empty_execution_id_validation(method, args):
    store = ExecutionEventStore()

    with pytest.raises(ValueError):
        getattr(store, method)(*args)


@pytest.mark.parametrize(
    "method,args",
    [
        ("get_events", ("   ",)),
        ("get_latest", ("   ",)),
        ("count", ("   ",)),
        ("has_events", ("   ",)),
        ("clear", ("   ",)),
    ],
)
def test_whitespace_execution_id_validation(method, args):
    store = ExecutionEventStore()

    with pytest.raises(ValueError):
        getattr(store, method)(*args)


# ============================================================
# Step ID Validation
# ============================================================


def test_step_id_validation():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.get_step_events(
            "exec-001",
            123,
        )


def test_step_id_none_validation():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.get_step_events(
            "exec-001",
            None,
        )


def test_empty_step_id_validation():
    store = ExecutionEventStore()

    with pytest.raises(ValueError):
        store.get_step_events(
            "exec-001",
            "",
        )


def test_whitespace_step_id_validation():
    store = ExecutionEventStore()

    with pytest.raises(ValueError):
        store.get_step_events(
            "exec-001",
            "   ",
        )


def test_get_step_events_validates_execution_id_first():
    store = ExecutionEventStore()

    with pytest.raises(TypeError):
        store.get_step_events(
            None,
            "step-001",
        )


# ============================================================
# Store Isolation
# ============================================================


def test_events_are_isolated_by_execution_id():
    store = ExecutionEventStore()

    first = make_event(
        "exec-001",
        ExecutionEventType.EXECUTION_STARTED,
    )

    second = make_event(
        "exec-002",
        ExecutionEventType.EXECUTION_STARTED,
    )

    store.record(first)
    store.record(second)

    assert store.get_events("exec-001") == [first]
    assert store.get_events("exec-002") == [second]


def test_clearing_one_execution_does_not_affect_other_events():
    store = ExecutionEventStore()

    events = [
        make_event("exec-001"),
        make_event("exec-002"),
        make_event(
            "exec-001",
            ExecutionEventType.EXECUTION_COMPLETED,
        ),
        make_event(
            "exec-002",
            ExecutionEventType.EXECUTION_COMPLETED,
        ),
    ]

    store.record_many(events)

    store.clear("exec-001")

    assert store.get_events("exec-001") == []

    assert store.get_events("exec-002") == [
        events[1],
        events[3],
    ]


# ============================================================
# Event Identity / Immutability
# ============================================================


def test_store_preserves_event_identity():
    store = ExecutionEventStore()

    event = make_event()

    returned = store.record(event)

    assert returned is event
    assert store.get_events("exec-001")[0] is event


def test_store_does_not_modify_event():
    store = ExecutionEventStore()

    event = make_event(
        event_type=ExecutionEventType.STEP_STARTED,
        step_id="step-001",
        step_index=0,
    )

    before = event.to_dict()

    store.record(event)

    after = event.to_dict()

    assert after == before
