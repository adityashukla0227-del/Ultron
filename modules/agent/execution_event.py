"""
Ultron Agent Execution Event Model

Defines structured events emitted during agent execution.

v0.44 — Agent Execution Observability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExecutionEventType(str, Enum):
    """Types of events emitted during agent execution."""

    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"

    EXECUTION_PAUSED = "execution_paused"
    EXECUTION_RESUMED = "execution_resumed"
    EXECUTION_CANCELLED = "execution_cancelled"

    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_RETRIED = "step_retried"
    STEP_SKIPPED = "step_skipped"


@dataclass(frozen=True)
class ExecutionEvent:
    """
    Immutable structured event produced during agent execution.

    An event represents a single observable change in an execution
    lifecycle or step lifecycle.
    """

    event_type: ExecutionEventType
    execution_id: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    step_id: str | None = None
    step_index: int | None = None

    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize event data."""

        # ====================================================
        # Event Type
        # ====================================================

        if isinstance(self.event_type, str):
            try:
                object.__setattr__(
                    self,
                    "event_type",
                    ExecutionEventType(self.event_type),
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid execution event type: "
                    f"{self.event_type}"
                ) from exc

        elif not isinstance(
            self.event_type,
            ExecutionEventType,
        ):
            raise TypeError(
                "event_type must be an ExecutionEventType"
            )

        # ====================================================
        # Execution ID
        # ====================================================

        if not isinstance(
            self.execution_id,
            str,
        ):
            raise TypeError(
                "execution_id must be a string"
            )

        if not self.execution_id.strip():
            raise ValueError(
                "execution_id cannot be empty"
            )

        # ====================================================
        # Timestamp
        # ====================================================

        if not isinstance(
            self.timestamp,
            datetime,
        ):
            raise TypeError(
                "timestamp must be a datetime"
            )

        # ====================================================
        # Step ID
        # ====================================================

        if self.step_id is not None and not isinstance(
            self.step_id,
            str,
        ):
            raise TypeError(
                "step_id must be a string or None"
            )

        # ====================================================
        # Step Index
        # ====================================================

        if self.step_index is not None:

            if not isinstance(
                self.step_index,
                int,
            ):
                raise TypeError(
                    "step_index must be an integer or None"
                )

            if self.step_index < 0:
                raise ValueError(
                    "step_index cannot be negative"
                )

        # ====================================================
        # Message
        # ====================================================

        if self.message is not None and not isinstance(
            self.message,
            str,
        ):
            raise TypeError(
                "message must be a string or None"
            )

        # ====================================================
        # Metadata
        # ====================================================

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    # ========================================================
    # Classification
    # ========================================================

    @property
    def is_execution_event(self) -> bool:
        """Return True when the event belongs to execution lifecycle."""

        return self.event_type in {
            ExecutionEventType.EXECUTION_STARTED,
            ExecutionEventType.EXECUTION_COMPLETED,
            ExecutionEventType.EXECUTION_FAILED,
            ExecutionEventType.EXECUTION_PAUSED,
            ExecutionEventType.EXECUTION_RESUMED,
            ExecutionEventType.EXECUTION_CANCELLED,
        }

    @property
    def is_step_event(self) -> bool:
        """Return True when the event belongs to step lifecycle."""

        return self.event_type in {
            ExecutionEventType.STEP_STARTED,
            ExecutionEventType.STEP_COMPLETED,
            ExecutionEventType.STEP_FAILED,
            ExecutionEventType.STEP_RETRIED,
            ExecutionEventType.STEP_SKIPPED,
        }

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the event into a JSON-compatible dictionary.
        """

        return {
            "event_type": self.event_type.value,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "step_id": self.step_id,
            "step_index": self.step_index,
            "message": self.message,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExecutionEvent":
        """
        Create an ExecutionEvent from serialized data.

        Required fields:
            event_type
            execution_id

        Optional fields:
            timestamp
            step_id
            step_index
            message
            metadata
        """

        # ====================================================
        # Input Validation
        # ====================================================

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "data must be a dictionary"
            )

        # ====================================================
        # Event Type
        # ====================================================

        event_type = data.get(
            "event_type"
        )

        if isinstance(
            event_type,
            str,
        ):
            event_type = ExecutionEventType(
                event_type
            )

        elif not isinstance(
            event_type,
            ExecutionEventType,
        ):
            raise TypeError(
                "event_type must be an ExecutionEventType"
            )

        # ====================================================
        # Required Execution ID
        # ====================================================
        #
        # Intentionally use [] instead of .get().
        #
        # This preserves the distinction between:
        #
        #   missing execution_id -> KeyError
        #
        #   execution_id=None -> TypeError
        #
        #   execution_id="" -> ValueError
        #

        execution_id = data[
            "execution_id"
        ]

        # ====================================================
        # Timestamp
        # ====================================================

        timestamp = data.get(
            "timestamp"
        )

        if isinstance(
            timestamp,
            str,
        ):
            timestamp = datetime.fromisoformat(
                timestamp
            )

        elif timestamp is not None and not isinstance(
            timestamp,
            datetime,
        ):
            raise TypeError(
                "timestamp must be a datetime, "
                "ISO-formatted string, or None"
            )

        if timestamp is None:
            timestamp = datetime.now(
                timezone.utc
            )

        # ====================================================
        # Metadata
        # ====================================================

        metadata = data.get(
            "metadata"
        )

        if metadata is None:
            metadata = {}
        elif not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )
        else:
            metadata = dict(
                metadata
            )

        # ====================================================
        # Construct Event
        # ====================================================

        return cls(
            event_type=event_type,
            execution_id=execution_id,
            timestamp=timestamp,
            step_id=data.get(
                "step_id"
            ),
            step_index=data.get(
                "step_index"
            ),
            message=data.get(
                "message"
            ),
            metadata=metadata,
        )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "ExecutionEvent("
            f"event_type='{self.event_type.value}', "
            f"execution_id='{self.execution_id}', "
            f"step_id='{self.step_id}', "
            f"step_index={self.step_index}"
            ")"
        )


__all__ = [
    "ExecutionEvent",
    "ExecutionEventType",
]