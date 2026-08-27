"""
Ultron Execution State Snapshot.

v0.48 — Execution Recovery & State Restoration

Defines an immutable snapshot of an execution's recoverable state.

The snapshot represents a point-in-time description of execution
progress without coupling state representation to the execution
controller, event store, persistence layer, or recovery manager.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class ExecutionStateSnapshotError(ValueError):
    """Base exception for execution state snapshot errors."""


@dataclass(frozen=True)
class ExecutionStateSnapshot:
    """
    Immutable representation of recoverable execution state.

    The snapshot captures execution identity, lifecycle status,
    current execution position, progress counters, retry activity,
    and the time at which the snapshot was created.

    The snapshot is descriptive only. It does not execute, resume,
    pause, cancel, retry, or otherwise modify an execution.
    """

    execution_id: str

    status: str

    current_step_id: str | None = None

    current_step_index: int | None = None

    completed_steps: int = 0

    failed_steps: int = 0

    pending_steps: int = 0

    retry_count: int = 0

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate snapshot data."""

        # ----------------------------------------------------
        # Execution ID
        # ----------------------------------------------------

        if not isinstance(
            self.execution_id,
            str,
        ):
            raise TypeError(
                "execution_id must be a string."
            )

        if not self.execution_id.strip():
            raise ValueError(
                "execution_id cannot be empty."
            )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if not isinstance(
            self.status,
            str,
        ):
            raise TypeError(
                "status must be a string."
            )

        if not self.status.strip():
            raise ValueError(
                "status cannot be empty."
            )

        supported_statuses = {
            "pending",
            "running",
            "paused",
            "completed",
            "failed",
            "cancelled",
        }

        if self.status not in supported_statuses:
            raise ValueError(
                f"Unsupported status: {self.status}"
            )

        # ----------------------------------------------------
        # Current Step
        # ----------------------------------------------------

        if self.current_step_id is not None:
            if not isinstance(
                self.current_step_id,
                str,
            ):
                raise TypeError(
                    "current_step_id must be a string or None."
                )

            if not self.current_step_id.strip():
                raise ValueError(
                    "current_step_id cannot be empty."
                )

        # ----------------------------------------------------
        # Current Step Index
        # ----------------------------------------------------

        if self.current_step_index is not None:
            if not isinstance(
                self.current_step_index,
                int,
            ):
                raise TypeError(
                    "current_step_index must be an integer or None."
                )

            if self.current_step_index < 0:
                raise ValueError(
                    "current_step_index cannot be negative."
                )

        # ----------------------------------------------------
        # Step Counters
        # ----------------------------------------------------

        counters = {
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "pending_steps": self.pending_steps,
            "retry_count": self.retry_count,
        }

        for field_name, value in counters.items():
            if not isinstance(
                value,
                int,
            ):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        if not isinstance(
            self.timestamp,
            datetime,
        ):
            raise TypeError(
                "timestamp must be a datetime."
            )

    # ========================================================
    # Derived State
    # ========================================================

    @property
    def is_completed(self) -> bool:
        """Return True when the execution is completed."""

        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Return True when the execution has failed."""

        return self.status == "failed"

    @property
    def is_paused(self) -> bool:
        """Return True when the execution is paused."""

        return self.status == "paused"

    @property
    def is_cancelled(self) -> bool:
        """Return True when the execution is cancelled."""

        return self.status == "cancelled"

    @property
    def is_running(self) -> bool:
        """Return True when the execution is running."""

        return self.status == "running"

    @property
    def is_pending(self) -> bool:
        """Return True when the execution is pending."""

        return self.status == "pending"

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the snapshot into a JSON-compatible dictionary.

        A new dictionary is returned on every call.
        """

        return {
            "execution_id": self.execution_id,
            "status": self.status,
            "current_step_id": self.current_step_id,
            "current_step_index": self.current_step_index,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "pending_steps": self.pending_steps,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExecutionStateSnapshot":
        """
        Reconstruct an ExecutionStateSnapshot from serialized data.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "data must be a dictionary."
            )

        execution_id = data.get("execution_id")

        if execution_id is None:
            raise ValueError(
                "execution_id is required."
            )

        status = data.get("status")

        if status is None:
            raise ValueError(
                "status is required."
            )

        timestamp = data.get("timestamp")

        if isinstance(
            timestamp,
            str,
        ):
            try:
                timestamp = datetime.fromisoformat(
                    timestamp
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid timestamp: {exc}"
                ) from exc

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        return cls(
            execution_id=execution_id,
            status=status,
            current_step_id=data.get(
                "current_step_id"
            ),
            current_step_index=data.get(
                "current_step_index"
            ),
            completed_steps=data.get(
                "completed_steps",
                0,
            ),
            failed_steps=data.get(
                "failed_steps",
                0,
            ),
            pending_steps=data.get(
                "pending_steps",
                0,
            ),
            retry_count=data.get(
                "retry_count",
                0,
            ),
            timestamp=timestamp,
        )


__all__ = [
    "ExecutionStateSnapshot",
    "ExecutionStateSnapshotError",
]