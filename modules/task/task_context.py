"""
Ultron Task Context
Version: v0.81

Provides task-scoped contextual information and mutable state.

Responsibilities:
- Hold the associated Task
- Hold task-scoped context data
- Hold task-scoped state
- Provide controlled task context access
- Provide controlled task state access
- Provide defensive copies of task data
- Validate task context structure
- Provide safe serialization

The TaskContext does NOT:
- Execute tasks
- Manage task lifecycle
- Select tools
- Select agents
- Create execution plans
- Track execution progress
- Handle retries
- Handle cancellation
- Handle timeouts
- Store execution results
- Call AI providers
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from modules.task.task import Task


class TaskContextError(Exception):
    """Base exception for task context errors."""


class TaskContext:
    """
    Task-scoped context and state container.

    The TaskContext belongs to a logical Task and remains
    separate from execution-level runtime context.
    """

    def __init__(
        self,
        task: Task,
        *,
        context: Dict[str, Any] | None = None,
        state: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a task context.
        """

        if not isinstance(task, Task):
            raise TaskContextError(
                "task must be a Task instance."
            )

        self.task = task
        self.context: Dict[str, Any] = dict(
            context or {}
        )
        self.state: Dict[str, Any] = dict(
            state or {}
        )

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """Validate the task context structure."""

        if not isinstance(
            self.task,
            Task,
        ):
            raise TaskContextError(
                "task must be a Task instance."
            )

        if not isinstance(
            self.context,
            dict,
        ):
            raise TaskContextError(
                "context must be a dictionary."
            )

        if not isinstance(
            self.state,
            dict,
        ):
            raise TaskContextError(
                "state must be a dictionary."
            )

        return True

    # ========================================================
    # Context
    # ========================================================

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a task-scoped context value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "context key must be a non-empty string."
            )

        self.context[key] = value

    def get_context(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get a task-scoped context value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "context key must be a non-empty string."
            )

        return self.context.get(
            key,
            default,
        )

    def remove_context(
        self,
        key: str,
    ) -> bool:
        """Remove a task-scoped context value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "context key must be a non-empty string."
            )

        if key not in self.context:
            return False

        del self.context[key]

        return True

    def get_all_context(self) -> Dict[str, Any]:
        """Return a defensive copy of all task context data."""

        return deepcopy(
            self.context
        )

    # ========================================================
    # State
    # ========================================================

    def set_state(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a task-scoped state value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "state key must be a non-empty string."
            )

        self.state[key] = value

    def get_state(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get a task-scoped state value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "state key must be a non-empty string."
            )

        return self.state.get(
            key,
            default,
        )

    def remove_state(
        self,
        key: str,
    ) -> bool:
        """Remove a task-scoped state value."""

        if not isinstance(key, str) or not key.strip():
            raise TaskContextError(
                "state key must be a non-empty string."
            )

        if key not in self.state:
            return False

        del self.state[key]

        return True

    def get_all_state(self) -> Dict[str, Any]:
        """Return a defensive copy of all task state."""

        return deepcopy(
            self.state
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the task context.

        The associated Task is serialized through its
        existing to_dict() contract.
        """

        return {
            "task": self.task.to_dict(),
            "context": deepcopy(
                self.context
            ),
            "state": deepcopy(
                self.state
            ),
        }


__all__ = [
    "TaskContext",
    "TaskContextError",
]
