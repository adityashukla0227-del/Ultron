"""
Ultron Execution Result
Version: v0.83

Standardized result model for complete task execution outcomes.

Responsibilities:
- Represent the overall outcome of one execution
- Store execution identity
- Store success/failure state
- Store execution result data
- Store execution error information
- Store extensible execution metadata
- Validate execution result integrity
- Provide defensive serialization

The ExecutionResult does NOT:
- Execute tasks
- Execute tools
- Manage lifecycle
- Manage runtime state
- Emit events
- Handle retries or recovery
- Select tools
- Perform planning
- Provide execution feedback
"""


from dataclasses import dataclass
from copy import deepcopy
from typing import Any, Dict, Optional


class ExecutionResultError(ValueError):
    """Raised when an execution result is invalid."""


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable representation of one complete execution outcome.

    ExecutionResult represents the final outcome produced by
    an execution layer. It does not perform or control execution.
    """

    execution_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate and normalize the execution result."""

        if not isinstance(self.execution_id, str):
            raise ExecutionResultError(
                "execution_id must be a string."
            )

        if not self.execution_id.strip():
            raise ExecutionResultError(
                "execution_id must not be empty."
            )

        if not isinstance(self.success, bool):
            raise ExecutionResultError(
                "success must be a boolean."
            )

        if self.error is not None and not isinstance(
            self.error,
            str,
        ):
            raise ExecutionResultError(
                "error must be a string or None."
            )

        metadata = (
            deepcopy(self.metadata)
            if self.metadata is not None
            else {}
        )

        if not isinstance(metadata, dict):
            raise ExecutionResultError(
                "metadata must be a dictionary or None."
            )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    def validate(self) -> bool:
        """
        Validate execution result integrity.

        Returns:
            True when the result is valid.

        Raises:
            ExecutionResultError:
                When the execution result is invalid.
        """

        if not isinstance(self.execution_id, str):
            raise ExecutionResultError(
                "execution_id must be a string."
            )

        if not self.execution_id.strip():
            raise ExecutionResultError(
                "execution_id must not be empty."
            )

        if not isinstance(self.success, bool):
            raise ExecutionResultError(
                "success must be a boolean."
            )

        if self.error is not None and not isinstance(
            self.error,
            str,
        ):
            raise ExecutionResultError(
                "error must be a string or None."
            )

        if not isinstance(self.metadata, dict):
            raise ExecutionResultError(
                "metadata must be a dictionary."
            )

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the execution result into a dictionary.

        Returns a defensive copy so callers cannot mutate the
        internal metadata through the serialized representation.
        """

        return {
            "execution_id": self.execution_id,
            "success": self.success,
            "result": deepcopy(self.result),
            "error": self.error,
            "metadata": deepcopy(self.metadata),
        }