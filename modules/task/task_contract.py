"""
Ultron Task Contract
Version: v0.82

Binds a Task to its expected input and output contracts.

Responsibilities:
- Associate a Task with its input contract
- Associate a Task with its output contract
- Validate contract structure
- Provide defensive contract access
- Provide safe serialization

The TaskContract does NOT:
- Store actual task input data
- Store actual task output data
- Execute tasks
- Create execution results
- Manage task lifecycle
- Manage task context/state
- Select tools
- Select agents
- Create execution plans
- Call AI providers
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from modules.task.task import Task
from modules.task.task_input import TaskInputContract
from modules.task.task_output import TaskOutputContract


class TaskContractError(Exception):
    """Base exception for task contract errors."""


class TaskContract:
    """
    Associates a Task with its input and output contracts.
    """

    def __init__(
        self,
        task: Task,
        input_contract: TaskInputContract,
        output_contract: TaskOutputContract,
    ) -> None:
        self.task = task
        self.input_contract = input_contract
        self.output_contract = output_contract

        self.validate()

    def validate(self) -> bool:
        """
        Validate the complete task contract.
        """

        if not isinstance(
            self.task,
            Task,
        ):
            raise TaskContractError(
                "task must be a Task instance."
            )

        if not isinstance(
            self.input_contract,
            TaskInputContract,
        ):
            raise TaskContractError(
                "input_contract must be a TaskInputContract instance."
            )

        if not isinstance(
            self.output_contract,
            TaskOutputContract,
        ):
            raise TaskContractError(
                "output_contract must be a TaskOutputContract instance."
            )

        return True

    def get_input_contract(self) -> TaskInputContract:
        """
        Return the associated input contract.
        """

        return self.input_contract

    def get_output_contract(self) -> TaskOutputContract:
        """
        Return the associated output contract.
        """

        return self.output_contract

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task contract into a serializable dictionary.
        """

        return {
            "task": self.task.to_dict(),
            "input_contract": deepcopy(
                self.input_contract.to_dict()
            ),
            "output_contract": deepcopy(
                self.output_contract.to_dict()
            ),
        }


__all__ = [
    "TaskContract",
    "TaskContractError",
]