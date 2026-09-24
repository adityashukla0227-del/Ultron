"""
Ultron Execution Reliability

v0.89 — Execution Reliability

Provides deterministic validation of execution state snapshots.

This module does not:
- execute recovery
- mutate execution state
- control the execution controller
- emit events
- persist execution data
- execute tools
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.agent.execution_state_snapshot import (
    ExecutionStateSnapshot,
)


class ExecutionReliabilityError(Exception):
    """Base error for execution reliability operations."""


@dataclass(frozen=True)
class ExecutionReliabilityResult:
    """Result produced by execution reliability validation."""

    execution_id: str
    status: str
    valid: bool
    recoverable: bool
    reason: str


class ExecutionReliabilityValidator:
    """
    Deterministic validator for execution state snapshots.

    The validator is read-only and does not perform recovery,
    lifecycle transitions, controller operations, event emission,
    persistence, or tool execution.
    """

    RECOVERABLE_STATUSES = frozenset(
        {
            "running",
            "paused",
        }
    )

    TERMINAL_STATUSES = frozenset(
        {
            "completed",
            "cancelled",
        }
    )

    NON_RECOVERABLE_STATUSES = frozenset(
        {
            "pending",
            "failed",
        }
    )

    def validate(
        self,
        snapshot: ExecutionStateSnapshot,
    ) -> ExecutionReliabilityResult:
        """
        Validate an execution state snapshot.

        Returns a deterministic reliability result without
        modifying the supplied snapshot.
        """

        if not isinstance(snapshot, ExecutionStateSnapshot):
            raise TypeError(
                "snapshot must be an ExecutionStateSnapshot"
            )

        if snapshot.status in self.RECOVERABLE_STATUSES:
            return self._validate_recoverable(snapshot)

        if snapshot.status in self.TERMINAL_STATUSES:
            return self._validate_terminal(snapshot)

        if snapshot.status in self.NON_RECOVERABLE_STATUSES:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=True,
                recoverable=False,
                reason=(
                    "Execution is not recoverable from "
                    "its current lifecycle state."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=False,
            recoverable=False,
            reason="Execution status is not supported.",
        )

    def _validate_recoverable(
        self,
        snapshot: ExecutionStateSnapshot,
    ) -> ExecutionReliabilityResult:
        """Validate a recoverable execution state."""

        if snapshot.current_step_id is None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Recoverable execution must have "
                    "a current step."
                ),
            )

        if snapshot.current_step_index is None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Recoverable execution must have "
                    "a current step index."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=True,
            recoverable=True,
            reason="Execution state is valid and recoverable.",
        )

    def _validate_terminal(
        self,
        snapshot: ExecutionStateSnapshot,
    ) -> ExecutionReliabilityResult:
        """Validate a terminal execution state."""

        if snapshot.current_step_id is not None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Terminal execution must not "
                    "have a current step."
                ),
            )

        if snapshot.current_step_index is not None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Terminal execution must not "
                    "have a current step index."
                ),
            )

        if (
            snapshot.status == "completed"
            and snapshot.pending_steps != 0
        ):
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Completed execution must not "
                    "have pending steps."
                ),
            )

        if (
            snapshot.status == "completed"
            and snapshot.failed_steps != 0
        ):
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Completed execution must not "
                    "have failed steps."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=True,
            recoverable=False,
            reason="Execution has reached a terminal state.",
        )


__all__ = [
    "ExecutionReliabilityError",
    "ExecutionReliabilityResult",
    "ExecutionReliabilityValidator",
]
