"""
Ultron Task Abstraction
Version: v0.79

Core representation of a logical unit of work.

Responsibilities:
- Represent task identity
- Store task type
- Store task description
- Store task source
- Store task metadata
- Validate task state
- Provide safe serialization

The Task model does NOT:
- Execute tasks
- Select tools
- Select agents
- Create execution plans
- Manage task lifecycle
- Handle retries
- Handle cancellation
- Handle timeouts
- Call AI providers
- Orchestrate execution

Those responsibilities belong to later task/runtime layers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class TaskError(Exception):
    """Base exception for task errors."""


class TaskType(str, Enum):
    """
    High-level classification of a task.
    """

    ACTION = "action"
    PLANNING = "planning"
    AUTOMATION = "automation"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Task:
    """
    Immutable representation of a logical unit of work.
    """

    task_id: str
    task_type: TaskType
    description: str
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str):
            raise TypeError(
                "task_id must be a string"
            )

        if not self.task_id.strip():
            raise ValueError(
                "task_id must not be empty"
            )

        if not isinstance(self.task_type, TaskType):
            raise TypeError(
                "task_type must be a TaskType"
            )

        if not isinstance(self.description, str):
            raise TypeError(
                "description must be a string"
            )

        if not self.description.strip():
            raise ValueError(
                "description must not be empty"
            )

        if not isinstance(self.source, str):
            raise TypeError(
                "source must be a string"
            )

        if not isinstance(self.metadata, dict):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task into a serializable dictionary.
        """

        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "Task",
    "TaskError",
    "TaskType",
]