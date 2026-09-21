"""
Ultron Task Module
Version: v0.82

Provides the core Task abstraction, task lifecycle foundation,
task-scoped context/state, and task input/output contracts.
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

from .task_context import (
    TaskContext,
    TaskContextError,
)

from .task_input import (
    TaskInputContract,
    TaskInputContractError,
)

from .task_output import (
    TaskOutputContract,
    TaskOutputContractError,
)

from .task_contract import (
    TaskContract,
    TaskContractError,
)

__all__ = [
    "Task",
    "TaskError",
    "TaskType",
    "TaskLifecycle",
    "TaskLifecycleError",
    "TaskState",
    "TaskContext",
    "TaskContextError",
    "TaskInputContract",
    "TaskInputContractError",
    "TaskOutputContract",
    "TaskOutputContractError",
    "TaskContract",
    "TaskContractError",
]