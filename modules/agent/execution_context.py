"""
Ultron Agent Execution Context.

Provides centralized runtime context for an agent execution.

v0.50 — Execution Context Foundation
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict


class ExecutionContextError(Exception):
    """Base exception for execution context errors."""


class ExecutionContext:
    """
    Represents the runtime context of a single agent execution.

    The context keeps execution-scoped information in one place
    without taking ownership of execution lifecycle or event storage.

    Architecture:

        AgentPlan
            |
            v
        AgentOrchestrator
            |
            v
        ExecutionContext
            |
            +-------------------+
            |                   |
            v                   v
        Execution State    Execution Metadata
    """

    def __init__(
        self,
        execution_id: str,
        *,
        plan_id: str | None = None,
        agent_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an execution context.

        Parameters:
            execution_id:
                Stable identifier for the current execution.

            plan_id:
                Optional plan identifier.

            agent_id:
                Optional agent identifier.

            metadata:
                Optional execution-scoped metadata.
        """

        if not isinstance(
            execution_id,
            str,
        ) or not execution_id.strip():

            raise ExecutionContextError(
                "execution_id must be a non-empty string."
            )

        if plan_id is not None and not isinstance(
            plan_id,
            str,
        ):
            raise ExecutionContextError(
                "plan_id must be a string or None."
            )

        if agent_id is not None and not isinstance(
            agent_id,
            str,
        ):
            raise ExecutionContextError(
                "agent_id must be a string or None."
            )

        self.execution_id = execution_id
        self.plan_id = plan_id
        self.agent_id = agent_id

        self.status = "created"

        self.current_step_id: str | None = None
        self.current_step_index: int | None = None

        self.completed_steps = 0
        self.failed_steps = 0
        self.skipped_steps = 0
        self.retried_steps = 0
        self.total_steps = 0

        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

        self.metadata: Dict[str, Any] = dict(
            metadata or {}
        )

        self._results: Dict[str, Any] = {}

    # ========================================================
    # Lifecycle
    # ========================================================

    def start(self) -> None:
        """Mark the execution context as started."""

        if self.status == "completed":
            raise ExecutionContextError(
                "Cannot start a completed execution context."
            )

        self.status = "running"

        if self.started_at is None:
            self.started_at = datetime.now(
                timezone.utc
            )

    def pause(self) -> None:
        """Mark the execution context as paused."""

        if self.status != "running":
            raise ExecutionContextError(
                "Only a running execution can be paused."
            )

        self.status = "paused"

    def resume(self) -> None:
        """Resume a paused execution context."""

        if self.status != "paused":
            raise ExecutionContextError(
                "Only a paused execution can be resumed."
            )

        self.status = "running"

    def cancel(self) -> None:
        """Mark the execution context as cancelled."""

        if self.status in {
            "completed",
            "cancelled",
        }:
            raise ExecutionContextError(
                "Execution context cannot be cancelled in its current state."
            )

        self.status = "cancelled"

        self.current_step_id = None
        self.current_step_index = None

    def fail(self) -> None:
        """Mark the execution context as failed."""

        if self.status == "completed":
            raise ExecutionContextError(
                "A completed execution cannot be failed."
            )

        self.status = "failed"

        self.current_step_id = None
        self.current_step_index = None

    def complete(self) -> None:
        """Mark the execution context as completed."""

        if self.status in {
            "cancelled",
            "failed",
        }:
            raise ExecutionContextError(
                "A failed or cancelled execution cannot be completed."
            )

        self.status = "completed"

        self.completed_at = datetime.now(
            timezone.utc
        )

        self.current_step_id = None
        self.current_step_index = None

    # ========================================================
    # Step Tracking
    # ========================================================

    def set_total_steps(
        self,
        total_steps: int,
    ) -> None:
        """Set the total number of steps."""

        if not isinstance(
            total_steps,
            int,
        ):
            raise ExecutionContextError(
                "total_steps must be an integer."
            )

        if total_steps < 0:
            raise ExecutionContextError(
                "total_steps cannot be negative."
            )

        self.total_steps = total_steps

    def set_current_step(
        self,
        step_id: str,
        *,
        step_index: int | None = None,
    ) -> None:
        """Set the currently executing step."""

        if not isinstance(
            step_id,
            str,
        ) or not step_id.strip():

            raise ExecutionContextError(
                "step_id must be a non-empty string."
            )

        if step_index is not None and not isinstance(
            step_index,
            int,
        ):
            raise ExecutionContextError(
                "step_index must be an integer or None."
            )

        self.current_step_id = step_id
        self.current_step_index = step_index

    def clear_current_step(self) -> None:
        """Clear the currently executing step."""

        self.current_step_id = None
        self.current_step_index = None

    def record_completed_step(
        self,
        step_id: str,
        result: Any = None,
    ) -> None:
        """Record a completed step and its result."""

        self.completed_steps += 1

        self._results[step_id] = result

        self.clear_current_step()

    def record_failed_step(
        self,
        step_id: str,
        error: Any = None,
    ) -> None:
        """Record a failed step."""

        self.failed_steps += 1

        self._results[step_id] = {
            "error": error,
        }

        self.clear_current_step()

    def record_skipped_step(
        self,
        step_id: str,
    ) -> None:
        """Record a skipped step."""

        self.skipped_steps += 1

        self.clear_current_step()

    def record_retried_step(
        self,
        step_id: str,
    ) -> None:
        """Record a retried step."""

        self.retried_steps += 1

    # ========================================================
    # Results
    # ========================================================

    def set_result(
        self,
        step_id: str,
        result: Any,
    ) -> None:
        """Store a result for a step."""

        if not isinstance(
            step_id,
            str,
        ) or not step_id.strip():

            raise ExecutionContextError(
                "step_id must be a non-empty string."
            )

        self._results[step_id] = result

    def get_result(
        self,
        step_id: str,
        default: Any = None,
    ) -> Any:
        """Return a stored step result."""

        return self._results.get(
            step_id,
            default,
        )

    def get_results(self) -> Dict[str, Any]:
        """Return a defensive copy of all step results."""

        return deepcopy(
            self._results
        )

    # ========================================================
    # Context Queries
    # ========================================================

    def has_result(
        self,
        step_id: str,
    ) -> bool:
        """Return True when a result exists for the supplied step."""

        if not isinstance(
            step_id,
            str,
        ) or not step_id.strip():

            raise ExecutionContextError(
                "step_id must be a non-empty string."
            )

        return step_id in self._results

    def has_failed_steps(self) -> bool:
        """Return True when one or more steps have failed."""

        return self.failed_steps > 0

    def has_completed_steps(self) -> bool:
        """Return True when one or more steps have completed."""

        return self.completed_steps > 0

    def has_skipped_steps(self) -> bool:
        """Return True when one or more steps have been skipped."""

        return self.skipped_steps > 0

    def is_finished(self) -> bool:
        """
        Return True when execution has reached a terminal state.
        """

        return self.status in {
            "completed",
            "failed",
            "cancelled",
        }

    def get_last_result(
        self,
        default: Any = None,
    ) -> Any:
        """
        Return the most recently stored step result.

        Results preserve insertion order because the underlying
        storage uses a standard Python dictionary.
        """

        if not self._results:
            return default

        step_id = next(
            reversed(self._results)
        )

        return deepcopy(
            self._results[step_id]
        )

    def get_processed_steps(self) -> int:
        """Return the number of processed steps."""

        return (
            self.completed_steps
            + self.failed_steps
            + self.skipped_steps
        )

    def get_remaining_steps(self) -> int:
        """
        Return the number of remaining unprocessed steps.

        The value is never allowed to become negative.
        """

        return max(
            self.total_steps
            - self.get_processed_steps(),
            0,
        )

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set execution metadata."""

        if not isinstance(
            key,
            str,
        ) or not key.strip():

            raise ExecutionContextError(
                "metadata key must be a non-empty string."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return execution metadata."""

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of execution metadata."""

        return deepcopy(
            self.metadata
        )

    # ========================================================
    # State
    # ========================================================

    def is_created(self) -> bool:
        """Return True when the context has not started."""

        return self.status == "created"

    def is_running(self) -> bool:
        """Return True when execution is running."""

        return self.status == "running"

    def is_paused(self) -> bool:
        """Return True when execution is paused."""

        return self.status == "paused"

    def is_cancelled(self) -> bool:
        """Return True when execution is cancelled."""

        return self.status == "cancelled"

    def is_failed(self) -> bool:
        """Return True when execution has failed."""

        return self.status == "failed"

    def is_completed(self) -> bool:
        """Return True when execution is completed."""

        return self.status == "completed"

    def is_active(self) -> bool:
        """Return True when execution is active."""

        return self.status in {
            "running",
            "paused",
        }

    # ========================================================
    # Progress
    # ========================================================

    def get_progress(self) -> Dict[str, Any]:
        """Return execution progress information."""

        processed = self.get_processed_steps()

        percentage = 0.0

        if self.total_steps > 0:
            percentage = (
                processed
                / self.total_steps
            ) * 100

        return {
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "retried_steps": self.retried_steps,
            "processed_steps": processed,
            "percentage": percentage,
            "current_step_id": self.current_step_id,
            "current_step_index": self.current_step_index,
        }

    # ========================================================
    # Snapshot
    # ========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a complete defensive snapshot of the context.
        """

        return {
            "execution_id": self.execution_id,
            "plan_id": self.plan_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "current_step_id": self.current_step_id,
            "current_step_index": self.current_step_index,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "retried_steps": self.retried_steps,
            "total_steps": self.total_steps,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": deepcopy(
                self.metadata
            ),
            "results": deepcopy(
                self._results
            ),
            "progress": self.get_progress(),
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "ExecutionContext("
            f"execution_id={self.execution_id!r}, "
            f"plan_id={self.plan_id!r}, "
            f"agent_id={self.agent_id!r}, "
            f"status={self.status!r}, "
            f"current_step_id={self.current_step_id!r}"
            ")"
        )


__all__ = [
    "ExecutionContext",
    "ExecutionContextError",
]