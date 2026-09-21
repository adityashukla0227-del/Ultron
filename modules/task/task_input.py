"""
Ultron Task Input Contract
Version: v0.82

Defines the expected input contract for a Task.

Responsibilities:
- Store input contract identity
- Store input contract description
- Store expected input schema
- Validate contract structure
- Provide defensive schema access
- Provide safe serialization

The TaskInputContract does NOT:
- Store actual task input data
- Execute tasks
- Validate execution results
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


class TaskInputContractError(Exception):
    """Base exception for task input contract errors."""


class TaskInputContract:
    """
    Defines the expected input structure for a Task.
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
        Validate the complete input contract.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise TaskInputContractError(
                "name must be a string."
            )

        if not self.name.strip():
            raise TaskInputContractError(
                "name must not be empty."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TaskInputContractError(
                "description must be a string."
            )

        if not isinstance(
            self.schema,
            dict,
        ):
            raise TaskInputContractError(
                "schema must be a dictionary."
            )

        return True

    def get_schema(self) -> Dict[str, Any]:
        """
        Return a defensive copy of the input schema.
        """

        return deepcopy(
            self.schema
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the input contract into a serializable dictionary.
        """

        return {
            "name": self.name,
            "description": self.description,
            "schema": deepcopy(self.schema),
        }


__all__ = [
    "TaskInputContract",
    "TaskInputContractError",
]