"""
Ultron Execution Recovery Model

v0.88 — Recovery Architecture

Defines the structured representation of a recovery action and the
deterministic planning layer for recovery decisions.

This module does not:
- execute recovery
- mutate execution state
- control lifecycle
- emit events
- persist execution data
- execute tools
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from modules.agent.execution_failure import ExecutionFailure
from modules.agent.execution_reliability import (
    ExecutionReliabilityValidator,
)
from modules.agent.execution_state_snapshot import (
    ExecutionStateSnapshot,
)


class RecoveryAction(str, Enum):
    """Actions that a recovery workflow may request."""

    RESUME = "resume"
    RETRY = "retry"
    SKIP = "skip"
    ABORT = "abort"


@dataclass(frozen=True)
class ExecutionRecovery:
    """
    Immutable representation of a recovery decision.

    ExecutionRecovery describes what recovery action should be
    requested. It does not execute that action.
    """

    execution_id: str
    action: RecoveryAction
    reason: str
    step_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")

        if not isinstance(self.action, RecoveryAction):
            raise TypeError("action must be a RecoveryAction")

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")

        if self.step_id is not None and not isinstance(self.step_id, str):
            raise TypeError("step_id must be a string or None")

        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict or None")

        if self.action is RecoveryAction.RETRY and self.step_id is None:
            raise ValueError("step_id is required for retry recovery")

        if self.action is RecoveryAction.SKIP and self.step_id is None:
            raise ValueError("step_id is required for skip recovery")

    def to_dict(self) -> Dict[str, Any]:
        """Return a defensive dictionary representation."""

        return {
            "execution_id": self.execution_id,
            "action": self.action.value,
            "reason": self.reason,
            "step_id": self.step_id,
            "metadata": dict(self.metadata) if self.metadata is not None else None,
        }


class ExecutionRecoveryPlanner:
    """
    Deterministic planner for execution recovery decisions.

    The planner only decides which recovery action should be requested.
    It does not execute recovery, mutate state, control the controller,
    emit events, or persist execution data.
    """

    def __init__(
        self,
        validator: Optional[ExecutionReliabilityValidator] = None,
    ) -> None:
        self._validator = validator or ExecutionReliabilityValidator()

    def plan(
        self,
        snapshot: ExecutionStateSnapshot,
        failure: Optional[ExecutionFailure] = None,
    ) -> ExecutionRecovery:
        """
        Plan a deterministic recovery action from execution state
        and an optional failure description.
        """

        if not isinstance(snapshot, ExecutionStateSnapshot):
            raise TypeError("snapshot must be an ExecutionStateSnapshot")

        if failure is not None and not isinstance(failure, ExecutionFailure):
            raise TypeError("failure must be an ExecutionFailure or None")

        if failure is not None:
            if failure.execution_id != snapshot.execution_id:
                raise ValueError(
                    "failure execution_id must match snapshot execution_id"
                )

            if not failure.retryable:
                return ExecutionRecovery(
                    execution_id=snapshot.execution_id,
                    action=RecoveryAction.ABORT,
                    reason="The failure is not retryable.",
                )

        reliability = self._validator.validate(snapshot)

        if not reliability.recoverable:
            return ExecutionRecovery(
                execution_id=snapshot.execution_id,
                action=RecoveryAction.ABORT,
                reason="Execution state is not recoverable.",
            )

        if snapshot.status == "paused":
            return ExecutionRecovery(
                execution_id=snapshot.execution_id,
                action=RecoveryAction.RESUME,
                reason=(
                    "Execution is paused and can resume "
                    "from its preserved state."
                ),
                step_id=snapshot.current_step_id,
            )

        if snapshot.status == "running":
            if (
                failure is not None
                and failure.retryable
                and failure.step_id is not None
                and failure.step_id == snapshot.current_step_id
            ):
                return ExecutionRecovery(
                    execution_id=snapshot.execution_id,
                    action=RecoveryAction.RETRY,
                    reason="The current failed step is retryable.",
                    step_id=snapshot.current_step_id,
                )

            return ExecutionRecovery(
                execution_id=snapshot.execution_id,
                action=RecoveryAction.ABORT,
                reason=(
                    "No valid recovery action is available "
                    "for the running execution."
                ),
            )

        return ExecutionRecovery(
            execution_id=snapshot.execution_id,
            action=RecoveryAction.ABORT,
            reason="Execution cannot be recovered from its current state.",
        )


__all__ = [
    "ExecutionRecovery",
    "ExecutionRecoveryPlanner",
    "RecoveryAction",
]