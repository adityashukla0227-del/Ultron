"""
Ultron Task Lifecycle Tests
Version: v0.80
"""

import pytest

from modules.task.task import (
    Task,
    TaskType,
)

from modules.task.task_lifecycle import (
    TaskLifecycle,
    TaskLifecycleError,
    TaskState,
)


def create_task():
    return Task(
        task_id="task-001",
        task_type=TaskType.ACTION,
        description="Perform an action",
    )


def test_task_lifecycle_defaults_to_created():
    lifecycle = TaskLifecycle(create_task())

    assert lifecycle.state is TaskState.CREATED
    assert lifecycle.is_terminal is False


def test_task_lifecycle_preserves_task():
    task = create_task()
    lifecycle = TaskLifecycle(task)

    assert lifecycle.task is task


def test_created_can_transition_to_initialized():
    lifecycle = TaskLifecycle(create_task())

    assert lifecycle.can_transition(TaskState.INITIALIZED) is True

    lifecycle.transition(TaskState.INITIALIZED)

    assert lifecycle.state is TaskState.INITIALIZED


def test_initialized_can_transition_to_running():
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.INITIALIZED,
    )

    assert lifecycle.can_transition(TaskState.RUNNING) is True

    lifecycle.transition(TaskState.RUNNING)

    assert lifecycle.state is TaskState.RUNNING


@pytest.mark.parametrize(
    "target_state",
    [
        TaskState.PAUSED,
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
    ],
)
def test_running_supports_valid_terminal_and_pause_transitions(
    target_state,
):
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.RUNNING,
    )

    assert lifecycle.can_transition(target_state) is True

    lifecycle.transition(target_state)

    assert lifecycle.state is target_state


def test_paused_can_resume_to_running():
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.PAUSED,
    )

    assert lifecycle.can_transition(TaskState.RUNNING) is True

    lifecycle.transition(TaskState.RUNNING)

    assert lifecycle.state is TaskState.RUNNING


def test_paused_can_transition_to_cancelled():
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.PAUSED,
    )

    assert lifecycle.can_transition(TaskState.CANCELLED) is True

    lifecycle.transition(TaskState.CANCELLED)

    assert lifecycle.state is TaskState.CANCELLED


@pytest.mark.parametrize(
    "current_state,target_state",
    [
        (TaskState.CREATED, TaskState.RUNNING),
        (TaskState.CREATED, TaskState.COMPLETED),
        (TaskState.INITIALIZED, TaskState.COMPLETED),
        (TaskState.PAUSED, TaskState.COMPLETED),
        (TaskState.PAUSED, TaskState.FAILED),
        (TaskState.COMPLETED, TaskState.RUNNING),
        (TaskState.FAILED, TaskState.RUNNING),
        (TaskState.CANCELLED, TaskState.RUNNING),
    ],
)
def test_invalid_task_lifecycle_transitions_are_rejected(
    current_state,
    target_state,
):
    lifecycle = TaskLifecycle(
        create_task(),
        state=current_state,
    )

    assert lifecycle.can_transition(target_state) is False

    with pytest.raises(TaskLifecycleError):
        lifecycle.transition(target_state)


@pytest.mark.parametrize(
    "terminal_state",
    [
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
    ],
)
def test_terminal_states_are_terminal(terminal_state):
    lifecycle = TaskLifecycle(
        create_task(),
        state=terminal_state,
    )

    assert lifecycle.is_terminal is True

    for target_state in TaskState:
        assert lifecycle.can_transition(target_state) is False


def test_target_state_must_be_task_state():
    lifecycle = TaskLifecycle(create_task())

    with pytest.raises(TypeError):
        lifecycle.can_transition("initialized")

    with pytest.raises(TypeError):
        lifecycle.transition("initialized")


def test_task_must_be_task_instance():
    with pytest.raises(TypeError):
        TaskLifecycle("not-a-task")


def test_initial_state_must_be_task_state():
    with pytest.raises(TypeError):
        TaskLifecycle(
            create_task(),
            state="created",
        )


def test_task_lifecycle_serialization():
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.RUNNING,
    )

    assert lifecycle.to_dict() == {
        "task_id": "task-001",
        "state": "running",
        "is_terminal": False,
    }


def test_terminal_task_lifecycle_serialization():
    lifecycle = TaskLifecycle(
        create_task(),
        state=TaskState.COMPLETED,
    )

    assert lifecycle.to_dict() == {
        "task_id": "task-001",
        "state": "completed",
        "is_terminal": True,
    }


def test_task_remains_immutable_through_lifecycle():
    task = create_task()
    lifecycle = TaskLifecycle(task)

    lifecycle.transition(TaskState.INITIALIZED)

    assert task.description == "Perform an action"
    assert task.task_id == "task-001"