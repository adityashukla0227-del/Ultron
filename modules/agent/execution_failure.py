"""
Ultron Execution Failure Model

v0.87 — Failure Handling Foundation

Defines the canonical structured representation of an execution failure.

This module does not:
- execute recovery
- retry executions
- mutate execution state
- emit events
- handle exceptions directly
- perform failure recovery
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class FailureScope(str, Enum):
    """Scope at which a failure occurred."""

    STEP = "step"
    EXECUTION = "execution"


class FailureCategory(str, Enum):
    """Canonical categories for execution failures."""

    EXCEPTION = "exception"
    TOOL_FAILURE = "tool_failure"
    STEP_FAILURE = "step_failure"
    EXECUTION_FAILURE = "execution_failure"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutionFailure:
    """
    Immutable structured representation of an execution failure.

    ExecutionFailure describes a failure. It does not handle the failure.
    """

    execution_id: str
    scope: FailureScope
    category: FailureCategory
    message: str
    retryable: bool
    step_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")

        if not isinstance(self.scope, FailureScope):
            raise TypeError("scope must be a FailureScope")

        if not isinstance(self.category, FailureCategory):
            raise TypeError("category must be a FailureCategory")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string")

        if not isinstance(self.retryable, bool):
            raise TypeError("retryable must be a bool")

        if self.step_id is not None and not isinstance(self.step_id, str):
            raise TypeError("step_id must be a string or None")

        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict or None")

        if self.scope is FailureScope.STEP and self.step_id is None:
            raise ValueError("step_id is required for step-scoped failures")

        if self.scope is FailureScope.EXECUTION and self.step_id is not None:
            raise ValueError(
                "step_id must be None for execution-scoped failures"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Return a defensive dictionary representation."""

        return {
            "execution_id": self.execution_id,
            "scope": self.scope.value,
            "category": self.category.value,
            "message": self.message,
            "retryable": self.retryable,
            "step_id": self.step_id,
            "metadata": dict(self.metadata) if self.metadata is not None else None,
        }