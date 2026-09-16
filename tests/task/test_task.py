"""
Ultron Task Tests
Version: v0.79
"""

import pytest

from modules.task.task import (
    Task,
    TaskError,
    TaskType,
)


def test_task_creation():
    task = Task(
        task_id="task-001",
        task_type=TaskType.ACTION,
        description="Send an email",
    )

    assert task.task_id == "task-001"
    assert task.task_type is TaskType.ACTION
    assert task.description == "Send an email"
    assert task.source == "unknown"
    assert task.metadata == {}


def test_task_supports_source():
    task = Task(
        task_id="task-002",
        task_type=TaskType.CONVERSATION,
        description="Answer the user",
        source="conversation",
    )

    assert task.source == "conversation"


def test_task_supports_metadata():
    task = Task(
        task_id="task-003",
        task_type=TaskType.AUTOMATION,
        description="Run scheduled automation",
        metadata={"priority": "high"},
    )

    assert task.metadata == {"priority": "high"}


def test_task_is_immutable():
    task = Task(
        task_id="task-004",
        task_type=TaskType.ACTION,
        description="Perform an action",
    )

    with pytest.raises(AttributeError):
        task.description = "Changed"


def test_task_id_must_be_string():
    with pytest.raises(TypeError):
        Task(
            task_id=123,
            task_type=TaskType.ACTION,
            description="Perform an action",
        )


def test_task_id_must_not_be_empty():
    with pytest.raises(ValueError):
        Task(
            task_id="",
            task_type=TaskType.ACTION,
            description="Perform an action",
        )


def test_task_type_must_be_task_type():
    with pytest.raises(TypeError):
        Task(
            task_id="task-005",
            task_type="action",
            description="Perform an action",
        )


def test_description_must_be_string():
    with pytest.raises(TypeError):
        Task(
            task_id="task-006",
            task_type=TaskType.ACTION,
            description=123,
        )


def test_description_must_not_be_empty():
    with pytest.raises(ValueError):
        Task(
            task_id="task-007",
            task_type=TaskType.ACTION,
            description="",
        )


def test_source_must_be_string():
    with pytest.raises(TypeError):
        Task(
            task_id="task-008",
            task_type=TaskType.ACTION,
            description="Perform an action",
            source=123,
        )


def test_metadata_must_be_dictionary():
    with pytest.raises(TypeError):
        Task(
            task_id="task-009",
            task_type=TaskType.ACTION,
            description="Perform an action",
            metadata=[],
        )


def test_task_serialization():
    task = Task(
        task_id="task-010",
        task_type=TaskType.PLANNING,
        description="Create an execution plan",
        source="agent_decision",
        metadata={"priority": "normal"},
    )

    assert task.to_dict() == {
        "task_id": "task-010",
        "task_type": "planning",
        "description": "Create an execution plan",
        "source": "agent_decision",
        "metadata": {"priority": "normal"},
    }


def test_task_metadata_is_copied_during_serialization():
    metadata = {"priority": "high"}

    task = Task(
        task_id="task-011",
        task_type=TaskType.ACTION,
        description="Perform an action",
        metadata=metadata,
    )

    serialized = task.to_dict()
    serialized["metadata"]["priority"] = "low"

    assert task.metadata["priority"] == "high"


@pytest.mark.parametrize(
    "task_type",
    [
        TaskType.ACTION,
        TaskType.PLANNING,
        TaskType.AUTOMATION,
        TaskType.CONVERSATION,
        TaskType.UNKNOWN,
    ],
)
def test_all_task_types_are_supported(task_type):
    task = Task(
        task_id="task-012",
        task_type=task_type,
        description="Test task",
    )

    assert task.task_type is task_type