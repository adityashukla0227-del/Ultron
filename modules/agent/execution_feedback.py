"""
Ultron Execution Feedback
Version: v0.84

Standardized consumer-facing feedback model for task execution.

Responsibilities:
- Represent execution feedback
- Store execution identity
- Store execution status
- Store human-readable feedback message
- Store execution progress
- Store execution result data
- Store execution error information
- Store extensible feedback metadata
- Validate feedback integrity
- Provide defensive serialization

The ExecutionFeedback does NOT:
- Execute tasks
- Execute tools
- Manage execution lifecycle
- Manage runtime state
- Emit execution events
- Handle retries or recovery
- Perform planning
- Select tools
- Create execution results
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional


class ExecutionFeedbackError(ValueError):
    """Raised when execution feedback is invalid."""


@dataclass(frozen=True)
class ExecutionFeedback:
    """
    Immutable representation of consumer-facing execution feedback.

    ExecutionFeedback describes how execution should be represented
    to a consumer without owning execution, lifecycle, or observability.
    """

    execution_id: str
    status: str
    message: Optional[str] = None
    progress: Dict[str, Any] | None = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate and normalize execution feedback."""

        # ====================================================
        # Execution ID
        # ====================================================

        if not isinstance(
            self.execution_id,
            str,
        ):
            raise ExecutionFeedbackError(
                "execution_id must be a string."
            )

        if not self.execution_id.strip():
            raise ExecutionFeedbackError(
                "execution_id must not be empty."
            )

        # ====================================================
        # Status
        # ====================================================

        if not isinstance(
            self.status,
            str,
        ):
            raise ExecutionFeedbackError(
                "status must be a string."
            )

        if not self.status.strip():
            raise ExecutionFeedbackError(
                "status must not be empty."
            )

        # ====================================================
        # Message
        # ====================================================

        if self.message is not None and not isinstance(
            self.message,
            str,
        ):
            raise ExecutionFeedbackError(
                "message must be a string or None."
            )

        # ====================================================
        # Result
        # ====================================================

        result = deepcopy(self.result)

        object.__setattr__(
            self,
            "result",
            result,
        )

        # ====================================================
        # Progress
        # ====================================================

        progress = (
            deepcopy(self.progress)
            if self.progress is not None
            else {}
        )

        if not isinstance(
            progress,
            dict,
        ):
            raise ExecutionFeedbackError(
                "progress must be a dictionary or None."
            )

        object.__setattr__(
            self,
            "progress",
            progress,
        )

        # ====================================================
        # Error
        # ====================================================

        if self.error is not None and not isinstance(
            self.error,
            str,
        ):
            raise ExecutionFeedbackError(
                "error must be a string or None."
            )

        # ====================================================
        # Metadata
        # ====================================================

        metadata = (
            deepcopy(self.metadata)
            if self.metadata is not None
            else {}
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ExecutionFeedbackError(
                "metadata must be a dictionary or None."
            )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate execution feedback integrity.

        Returns:
            True when the feedback is valid.

        Raises:
            ExecutionFeedbackError:
                When the feedback is invalid.
        """

        if not isinstance(
            self.execution_id,
            str,
        ):
            raise ExecutionFeedbackError(
                "execution_id must be a string."
            )

        if not self.execution_id.strip():
            raise ExecutionFeedbackError(
                "execution_id must not be empty."
            )

        if not isinstance(
            self.status,
            str,
        ):
            raise ExecutionFeedbackError(
                "status must be a string."
            )

        if not self.status.strip():
            raise ExecutionFeedbackError(
                "status must not be empty."
            )

        if self.message is not None and not isinstance(
            self.message,
            str,
        ):
            raise ExecutionFeedbackError(
                "message must be a string or None."
            )

        if not isinstance(
            self.progress,
            dict,
        ):
            raise ExecutionFeedbackError(
                "progress must be a dictionary."
            )

        if self.error is not None and not isinstance(
            self.error,
            str,
        ):
            raise ExecutionFeedbackError(
                "error must be a string or None."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ExecutionFeedbackError(
                "metadata must be a dictionary."
            )

        return True

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize execution feedback into a dictionary.

        Returns a defensive copy so callers cannot mutate the
        internal feedback state through the serialized result.
        """

        return {
            "execution_id": self.execution_id,
            "status": self.status,
            "message": self.message,
            "progress": deepcopy(self.progress),
            "result": deepcopy(self.result),
            "error": self.error,
            "metadata": deepcopy(self.metadata),
        }


__all__ = [
    "ExecutionFeedback",
    "ExecutionFeedbackError",
]
