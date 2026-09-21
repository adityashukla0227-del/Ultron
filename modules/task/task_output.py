"""
Ultron Task Output Contract
Version: v0.82

Defines the expected output contract for a Task.

Responsibilities:
- Store output contract identity
- Store output contract description
- Store expected output schema
- Validate contract structure
- Provide defensive schema access
- Provide safe serialization

The TaskOutputContract does NOT:
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


class TaskOutputContractError(Exception):
    """Base exception for task output contract errors."""


class TaskOutputContract:
    """
    Defines the expected output structure for a Task.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        schema: Dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.schema: Dict[str, Any] = deepcopy(
            schema or {}
        )

        self.validate()

    def validate(self) -> bool:
        """
        Validate the complete output contract.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise TaskOutputContractError(
                "name must be a string."
            )

        if not self.name.strip():
            raise TaskOutputContractError(
                "name must not be empty."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TaskOutputContractError(
                "description must be a string."
            )

        if not isinstance(
            self.schema,
            dict,
        ):
            raise TaskOutputContractError(
                "schema must be a dictionary."
            )

        return True

    def get_schema(self) -> Dict[str, Any]:
        """
        Return a defensive copy of the output schema.
        """

        return deepcopy(
            self.schema
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the output contract into a serializable dictionary.
        """

        return {
            "name": self.name,
            "description": self.description,
            "schema": deepcopy(self.schema),
        }


__all__ = [
    "TaskOutputContract",
    "TaskOutputContractError",
]