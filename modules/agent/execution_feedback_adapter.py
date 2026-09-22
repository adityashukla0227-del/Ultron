"""
Ultron Execution Feedback Adapter
Version: v0.84

Converts canonical ExecutionResult objects into standardized
consumer-facing ExecutionFeedback objects.

Responsibilities:
- Convert ExecutionResult into ExecutionFeedback
- Map execution success to feedback status
- Extract execution progress
- Preserve execution result and error information
- Preserve non-progress execution metadata

The ExecutionFeedbackAdapter does NOT:
- Execute tasks
- Execute tools
- Manage execution lifecycle
- Emit execution events
- Handle retries or recovery
- Perform planning
- Select tools
- Create or modify ExecutionResult
- Format voice, UI, or API-specific responses
"""

from copy import deepcopy

from modules.agent.execution_feedback import (
    ExecutionFeedback,
)
from modules.agent.execution_result import (
    ExecutionResult,
)


class ExecutionFeedbackAdapterError(ValueError):
    """Raised when execution feedback conversion fails."""


class ExecutionFeedbackAdapter:
    """
    Pure adapter from ExecutionResult to ExecutionFeedback.

    This adapter preserves the canonical ExecutionResult boundary
    while providing a standardized consumer-facing representation.
    """

    @staticmethod
    def from_execution_result(
        result: ExecutionResult,
    ) -> ExecutionFeedback:
        """
        Convert an ExecutionResult into ExecutionFeedback.

        Args:
            result:
                Canonical execution outcome.

        Returns:
            Consumer-facing ExecutionFeedback.

        Raises:
            ExecutionFeedbackAdapterError:
                When the supplied result is not an ExecutionResult.
        """

        if not isinstance(
            result,
            ExecutionResult,
        ):
            raise ExecutionFeedbackAdapterError(
                "result must be an ExecutionResult."
            )

        metadata = deepcopy(
            result.metadata
        )

        progress = metadata.pop(
            "progress",
            {},
        )

        if progress is None:
            progress = {}

        if not isinstance(
            progress,
            dict,
        ):
            raise ExecutionFeedbackAdapterError(
                "ExecutionResult progress metadata must be a dictionary."
            )

        status = (
            "completed"
            if result.success is True
            else "failed"
        )

        return ExecutionFeedback(
            execution_id=result.execution_id,
            status=status,
            message=None,
            progress=progress,
            result=deepcopy(result.result),
            error=result.error,
            metadata=metadata,
        )


__all__ = [
    "ExecutionFeedbackAdapter",
    "ExecutionFeedbackAdapterError",
]