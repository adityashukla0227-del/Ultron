"""
Ultron Execution Reliability Foundation.

v0.86 — Reliability Foundation

Provides deterministic validation of execution state
for future recovery workflows.

This module does not:
- execute plans
- mutate execution state
- control lifecycle
- emit events
- persist execution data
- perform recovery

It only evaluates whether an ExecutionStateSnapshot
is internally consistent and whether its lifecycle state
is recoverable under the v0.86 reliability contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.agent.execution_state_snapshot import (
    ExecutionStateSnapshot,
)


# ========================================================
# Errors
# ========================================================


class ExecutionReliabilityError(Exception):
    """Base error for execution reliability operations."""


# ========================================================
# Result
# ========================================================


@dataclass(frozen=True)
class ExecutionReliabilityResult:
    """
    Result of execution reliability validation.

    Attributes:
        execution_id: Execution identity.
        status: Execution lifecycle status.
        valid: Whether the snapshot is internally
            consistent for reliability purposes.
        recoverable: Whether the execution may be
            considered recoverable under v0.86 rules.
        reason: Deterministic explanation of the result.
    """

    execution_id: str
    status: str
    valid: bool
    recoverable: bool
    reason: str


# ========================================================
# Validator
# ========================================================


class ExecutionReliabilityValidator:
    """
    Validate execution-state reliability.

    The validator is intentionally read-only and has no
    orchestration, lifecycle, event, or persistence
    responsibilities.
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

        Args:
            snapshot: Immutable execution state snapshot.

        Returns:
            ExecutionReliabilityResult describing validity
            and recoverability.

        Raises:
            TypeError: If snapshot is not an
                ExecutionStateSnapshot.
        """

        if not isinstance(
            snapshot,
            ExecutionStateSnapshot,
        ):
            raise TypeError(
                "snapshot must be an ExecutionStateSnapshot."
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
                    f"Execution is in terminally "
                    f"non-recoverable state: "
                    f"{snapshot.status}."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=False,
            recoverable=False,
            reason=(
                f"Unsupported execution reliability "
                f"state: {snapshot.status}."
            ),
        )

    # ====================================================
    # Recoverable State Validation
    # ====================================================

    def _validate_recoverable(
        self,
        snapshot: ExecutionStateSnapshot,
    ) -> ExecutionReliabilityResult:
        """Validate a running or paused execution."""

        if snapshot.current_step_id is None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Recoverable execution must preserve "
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
                    "Recoverable execution must preserve "
                    "a current step index."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=True,
            recoverable=True,
            reason=(
                "Execution state is internally consistent "
                "and recoverable."
            ),
        )

    # ====================================================
    # Terminal State Validation
    # ====================================================

    def _validate_terminal(
        self,
        snapshot: ExecutionStateSnapshot,
    ) -> ExecutionReliabilityResult:
        """Validate a completed or cancelled execution."""

        if snapshot.current_step_id is not None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Terminal execution must not preserve "
                    "a current step."
                ),
            )

        if snapshot.current_step_index is not None:
            return ExecutionReliabilityResult(
                execution_id=snapshot.execution_id,
                status=snapshot.status,
                valid=False,
                recoverable=False,
                reason=(
                    "Terminal execution must not preserve "
                    "a current step index."
                ),
            )

        return ExecutionReliabilityResult(
            execution_id=snapshot.execution_id,
            status=snapshot.status,
            valid=True,
            recoverable=False,
            reason=(
                f"Execution is terminal: "
                f"{snapshot.status}."
            ),
        )


__all__ = [
    "ExecutionReliabilityError",
    "ExecutionReliabilityResult",
    "ExecutionReliabilityValidator",
]