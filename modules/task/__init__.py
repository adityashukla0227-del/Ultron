"""
Ultron Task Module
Version: v0.80

Provides the core Task abstraction, task types,
and task lifecycle foundation.
"""

from .task import (
    Task,
    TaskError,
    TaskType,
)

from .task_lifecycle import (
    TaskLifecycle,
    TaskLifecycleError,
    TaskState,
)

__all__ = [
    "Task",
    "TaskError",
    "TaskType",
    "TaskLifecycle",
    "TaskLifecycleError",
    "TaskState",
]