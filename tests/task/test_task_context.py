"""
Ultron Task Context Tests
Version: v0.81

Tests the task-scoped context and state foundation.
"""

from copy import deepcopy

import pytest

from modules.task.task import Task, TaskType
from modules.task.task_context import (
    TaskContext,
    TaskContextError,
)


@pytest.fixture
def task() -> Task:
    """Return a valid test task."""

    return Task(
        task_id="task-001",
        task_type=TaskType.ACTION,
        description="Test task",
        source="test",
    )


@pytest.fixture
def task_context(task: Task) -> TaskContext:
    """Return a default TaskContext."""

    return TaskContext(task)


# ============================================================
# Initialization
# ============================================================


def test_task_context_requires_task() -> None:
    """TaskContext must require a valid Task instance."""

    with pytest.raises(TaskContextError):
        TaskContext("invalid")  # type: ignore[arg-type]


def test_task_context_preserves_task(
    task: Task,
) -> None:
    """TaskContext must preserve the associated Task."""

    context = TaskContext(task)

    assert context.task is task


def test_task_context_default_context(
    task: Task,
) -> None:
    """TaskContext should start with empty context data."""

    context = TaskContext(task)

    assert context.context == {}


def test_task_context_default_state(
    task: Task,
) -> None:
    """TaskContext should start with empty state data."""

    context = TaskContext(task)

    assert context.state == {}


def test_task_context_initial_context_and_state(
    task: Task,
) -> None:
    """TaskContext should accept initial context and state."""

    context = TaskContext(
        task,
        context={"user": "Aditya"},
        state={"step": 1},
    )

    assert context.get_context("user") == "Aditya"
    assert context.get_state("step") == 1


def test_task_context_copies_initial_context(
    task: Task,
) -> None:
    """Initial context should not share the caller's dictionary."""

    source = {
        "nested": {
            "value": 1,
        }
    }

    context = TaskContext(
        task,
        context=source,
    )

    source["nested"]["value"] = 99

    assert context.get_context(
        "nested"
    )["value"] == 99


def test_task_context_copies_initial_state(
    task: Task,
) -> None:
    """Initial state should not share the caller's dictionary."""

    source = {
        "nested": {
            "value": 1,
        }
    }

    context = TaskContext(
        task,
        state=source,
    )

    source["nested"]["value"] = 99

    assert context.get_state(
        "nested"
    )["value"] == 99


# ============================================================
# Context Operations
# ============================================================


def test_set_and_get_context(
    task_context: TaskContext,
) -> None:
    """Context values should be set and retrieved."""

    task_context.set_context(
        "language",
        "Hindi",
    )

    assert task_context.get_context(
        "language"
    ) == "Hindi"


def test_get_context_default(
    task_context: TaskContext,
) -> None:
    """Missing context values should return the default."""

    assert task_context.get_context(
        "missing",
        "default",
    ) == "default"


def test_remove_context(
    task_context: TaskContext,
) -> None:
    """Context values should be removable."""

    task_context.set_context(
        "key",
        "value",
    )

    assert task_context.remove_context(
        "key"
    ) is True

    assert task_context.get_context(
        "key"
    ) is None


def test_remove_missing_context(
    task_context: TaskContext,
) -> None:
    """Removing a missing context value should return False."""

    assert task_context.remove_context(
        "missing"
    ) is False


@pytest.mark.parametrize(
    "method",
    [
        "set_context",
        "get_context",
        "remove_context",
    ],
)
def test_context_methods_reject_empty_keys(
    task_context: TaskContext,
    method: str,
) -> None:
    """Context methods must reject empty keys."""

    with pytest.raises(TaskContextError):
        if method == "set_context":
            task_context.set_context("", "value")
        elif method == "get_context":
            task_context.get_context("")
        else:
            task_context.remove_context("")


# ============================================================
# State Operations
# ============================================================


def test_set_and_get_state(
    task_context: TaskContext,
) -> None:
    """State values should be set and retrieved."""

    task_context.set_state(
        "progress",
        50,
    )

    assert task_context.get_state(
        "progress"
    ) == 50


def test_get_state_default(
    task_context: TaskContext,
) -> None:
    """Missing state values should return the default."""

    assert task_context.get_state(
        "missing",
        "default",
    ) == "default"


def test_remove_state(
    task_context: TaskContext,
) -> None:
    """State values should be removable."""

    task_context.set_state(
        "key",
        "value",
    )

    assert task_context.remove_state(
        "key"
    ) is True

    assert task_context.get_state(
        "key"
    ) is None


def test_remove_missing_state(
    task_context: TaskContext,
) -> None:
    """Removing a missing state value should return False."""

    assert task_context.remove_state(
        "missing"
    ) is False


@pytest.mark.parametrize(
    "method",
    [
        "set_state",
        "get_state",
        "remove_state",
    ],
)
def test_state_methods_reject_empty_keys(
    task_context: TaskContext,
    method: str,
) -> None:
    """State methods must reject empty keys."""

    with pytest.raises(TaskContextError):
        if method == "set_state":
            task_context.set_state("", "value")
        elif method == "get_state":
            task_context.get_state("")
        else:
            task_context.remove_state("")


# ============================================================
# Defensive Access
# ============================================================


def test_get_all_context_returns_copy(
    task_context: TaskContext,
) -> None:
    """All context data should be returned as a defensive copy."""

    task_context.set_context(
        "nested",
        {
            "value": 1,
        },
    )

    result = task_context.get_all_context()

    result["nested"]["value"] = 99

    assert task_context.get_context(
        "nested"
    )["value"] == 1


def test_get_all_state_returns_copy(
    task_context: TaskContext,
) -> None:
    """All state data should be returned as a defensive copy."""

    task_context.set_state(
        "nested",
        {
            "value": 1,
        },
    )

    result = task_context.get_all_state()

    result["nested"]["value"] = 99

    assert task_context.get_state(
        "nested"
    )["value"] == 1


# ============================================================
# Validation
# ============================================================


def test_validate_returns_true(
    task_context: TaskContext,
) -> None:
    """A valid TaskContext should validate successfully."""

    assert task_context.validate() is True


def test_validate_rejects_invalid_task(
    task_context: TaskContext,
) -> None:
    """Validation must reject an invalid Task reference."""

    task_context.task = "invalid"  # type: ignore[assignment]

    with pytest.raises(TaskContextError):
        task_context.validate()


def test_validate_rejects_invalid_context(
    task_context: TaskContext,
) -> None:
    """Validation must reject a non-dictionary context."""

    task_context.context = []  # type: ignore[assignment]

    with pytest.raises(TaskContextError):
        task_context.validate()


def test_validate_rejects_invalid_state(
    task_context: TaskContext,
) -> None:
    """Validation must reject a non-dictionary state."""

    task_context.state = []  # type: ignore[assignment]

    with pytest.raises(TaskContextError):
        task_context.validate()


# ============================================================
# Serialization
# ============================================================


def test_to_dict(
    task: Task,
) -> None:
    """TaskContext should serialize safely."""

    context = TaskContext(
        task,
        context={
            "language": "Hindi",
        },
        state={
            "step": 1,
        },
    )

    result = context.to_dict()

    assert result == {
        "task": task.to_dict(),
        "context": {
            "language": "Hindi",
        },
        "state": {
            "step": 1,
        },
    }


def test_to_dict_returns_defensive_data(
    task: Task,
) -> None:
    """Serialized data should not mutate the TaskContext."""

    context = TaskContext(
        task,
        context={
            "nested": {
                "value": 1,
            }
        },
        state={
            "nested": {
                "value": 2,
            }
        },
    )

    result = context.to_dict()

    result["context"]["nested"]["value"] = 99
    result["state"]["nested"]["value"] = 99

    assert context.get_context(
        "nested"
    )["value"] == 1

    assert context.get_state(
        "nested"
    )["value"] == 2


# ============================================================
# Task Boundary
# ============================================================


def test_task_remains_unchanged(
    task: Task,
) -> None:
    """TaskContext must not mutate the immutable Task."""

    original = deepcopy(
        task.to_dict()
    )

    context = TaskContext(task)

    context.set_context(
        "key",
        "value",
    )

    context.set_state(
        "status",
        "active",
    )

    assert task.to_dict() == original


def test_context_and_state_are_independent(
    task_context: TaskContext,
) -> None:
    """Context and state must remain separate containers."""

    task_context.set_context(
        "shared_name",
        "context_value",
    )

    task_context.set_state(
        "shared_name",
        "state_value",
    )

    assert task_context.get_context(
        "shared_name"
    ) == "context_value"

    assert task_context.get_state(
        "shared_name"
    ) == "state_value"
