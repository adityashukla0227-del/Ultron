"""
Ultron Task Lifecycle
Version: v0.80

Defines the lifecycle state machine for logical tasks.

Responsibilities:
- Represent task lifecycle state
- Validate lifecycle transitions
- Enforce valid state changes
- Detect terminal task states
- Provide safe serialization

The TaskLifecycle does NOT:
- Execute tasks
- Select tools
- Select agents
- Create execution plans
- Manage execution state
- Handle retries
- Handle recovery
- Handle timeouts
- Persist events
- Call AI providers
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict

from modules.task.task import Task


class TaskLifecycleError(ValueError):
    """Base exception for task lifecycle errors."""


class TaskState(str, Enum):
    """
    Lifecycle states for a logical task.
    """

    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskLifecycle:
    """
    Controlled lifecycle state machine for a Task.

    The lifecycle owns task state and transition rules,
    while the Task model remains immutable and descriptive.
    """

    _TRANSITIONS = {
        TaskState.CREATED: {
            TaskState.INITIALIZED,
        },
        TaskState.INITIALIZED: {
            TaskState.RUNNING,
        },
        TaskState.RUNNING: {
            TaskState.PAUSED,
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        },
        TaskState.PAUSED: {
            TaskState.RUNNING,
            TaskState.CANCELLED,
        },
        TaskState.COMPLETED: set(),
        TaskState.FAILED: set(),
        TaskState.CANCELLED: set(),
    }

    def __init__(
        self,
        task: Task,
        state: TaskState = TaskState.CREATED,
    ) -> None:
        """
        Initialize a lifecycle for a Task.
        """

        if not isinstance(
            task,
            Task,
        ):
            raise TypeError(
                "task must be a Task instance"
            )

        if not isinstance(
            state,
            TaskState,
        ):
            raise TypeError(
                "state must be a TaskState"
            )

        self._task = task
        self._state = state

    @property
    def task(self) -> Task:
        """
        Return the associated immutable Task.
        """

        return self._task

    @property
    def state(self) -> TaskState:
        """
        Return the current lifecycle state.
        """

        return self._state

    @property
    def is_terminal(self) -> bool:
        """
        Return True when the task has reached a terminal state.
        """

        return self._state in {
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        }

    def can_transition(
        self,
        target_state: TaskState,
    ) -> bool:
        """
        Return True when a transition to target_state is valid.
        """

        if not isinstance(
            target_state,
            TaskState,
        ):
            raise TypeError(
                "target_state must be a TaskState"
            )

        return target_state in self._TRANSITIONS[
            self._state
        ]

    def transition(
        self,
        target_state: TaskState,
    ) -> TaskState:
        """
        Transition the task to a new lifecycle state.
        """

        if not isinstance(
            target_state,
            TaskState,
        ):
            raise TypeError(
                "target_state must be a TaskState"
            )

        if not self.can_transition(
            target_state
        ):
            raise TaskLifecycleError(
                f"Invalid task lifecycle transition: "
                f"{self._state.value} -> "
                f"{target_state.value}"
            )

        self._state = target_state

        return self._state

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the current task lifecycle state.
        """

        return {
            "task_id": self._task.task_id,
            "state": self._state.value,
            "is_terminal": self.is_terminal,
        }


__all__ = [
    "TaskLifecycle",
    "TaskLifecycleError",
    "TaskState",
]