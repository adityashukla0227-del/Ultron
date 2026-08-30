"""
Ultron Agent Execution Event Emitter.

Creates and emits structured execution events.

v0.44 — Agent Execution Observability
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from .execution_event_store import (
    ExecutionEventStore,
    _CLEAR_ALL,
)


class ExecutionEventEmitter:
    """
    Emits structured events into an ExecutionEventStore.

    The emitter is responsible for creating ExecutionEvent objects.
    The store is responsible for retaining them.

    Architecture:

        Agent Execution
              |
              v
        ExecutionEventEmitter
              |
              v
        ExecutionEvent
              |
              v
        ExecutionEventStore
    """

    def __init__(
        self,
        store: ExecutionEventStore | None = None,
    ) -> None:
        """
        Initialize the event emitter.

        A store can be injected for testing or shared usage.
        """

        self.store = (
            store
            if store is not None
            else ExecutionEventStore()
        )

    # ========================================================
    # Core Emit
    # ========================================================

    def emit(
        self,
        event_type: ExecutionEventType,
        execution_id: str,
        *,
        step_id: str | None = None,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> ExecutionEvent:
        """
        Create and record an execution event.

        Returns the emitted ExecutionEvent.
        """

        if not isinstance(
            event_type,
            ExecutionEventType,
        ):
            raise TypeError(
                "event_type must be an ExecutionEventType"
            )

        event = ExecutionEvent(
            event_type=event_type,
            execution_id=execution_id,
            timestamp=(
                timestamp
                if timestamp is not None
                else datetime.now(timezone.utc)
            ),
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=dict(metadata or {}),
        )

        return self.store.record(event)

    # ========================================================
    # Execution Lifecycle
    # ========================================================

    def execution_started(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_started event."""

        return self.emit(
            ExecutionEventType.EXECUTION_STARTED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    def execution_completed(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_completed event."""

        return self.emit(
            ExecutionEventType.EXECUTION_COMPLETED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    def execution_failed(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_failed event."""

        return self.emit(
            ExecutionEventType.EXECUTION_FAILED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    def execution_paused(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_paused event."""

        return self.emit(
            ExecutionEventType.EXECUTION_PAUSED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    def execution_resumed(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_resumed event."""

        return self.emit(
            ExecutionEventType.EXECUTION_RESUMED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    def execution_cancelled(
        self,
        execution_id: str,
        *,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit an execution_cancelled event."""

        return self.emit(
            ExecutionEventType.EXECUTION_CANCELLED,
            execution_id,
            message=message,
            metadata=metadata,
        )

    # ========================================================
    # Step Lifecycle
    # ========================================================

    def step_started(
        self,
        execution_id: str,
        step_id: str,
        *,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit a step_started event."""

        return self.emit(
            ExecutionEventType.STEP_STARTED,
            execution_id,
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=metadata,
        )

    def step_completed(
        self,
        execution_id: str,
        step_id: str,
        *,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit a step_completed event."""

        return self.emit(
            ExecutionEventType.STEP_COMPLETED,
            execution_id,
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=metadata,
        )

    def step_failed(
        self,
        execution_id: str,
        step_id: str,
        *,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit a step_failed event."""

        return self.emit(
            ExecutionEventType.STEP_FAILED,
            execution_id,
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=metadata,
        )

    def step_retried(
        self,
        execution_id: str,
        step_id: str,
        *,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit a step_retried event."""

        return self.emit(
            ExecutionEventType.STEP_RETRIED,
            execution_id,
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=metadata,
        )

    def step_skipped(
        self,
        execution_id: str,
        step_id: str,
        *,
        step_index: int | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Emit a step_skipped event."""

        return self.emit(
            ExecutionEventType.STEP_SKIPPED,
            execution_id,
            step_id=step_id,
            step_index=step_index,
            message=message,
            metadata=metadata,
        )

    # ========================================================
    # Store Access
    # ========================================================

    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """Return all events for an execution."""

        return self.store.get_events(
            execution_id
        )

    def get_latest(
        self,
        execution_id: str,
    ) -> ExecutionEvent | None:
        """Return the latest event for an execution."""

        return self.store.get_latest(
            execution_id
        )

    def get_step_events(
        self,
        execution_id: str,
        step_id: str,
    ) -> list[ExecutionEvent]:
        """Return all events for a specific step."""

        return self.store.get_step_events(
            execution_id,
            step_id,
        )

    def count(
        self,
        execution_id: str,
    ) -> int:
        """Return the number of events for an execution."""

        return self.store.count(
            execution_id
        )

    def clear(
        self,
        execution_id: str | object = _CLEAR_ALL,
    ) -> None:
        """Clear stored events."""

        self.store.clear(
            execution_id
        )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "ExecutionEventEmitter("
            f"store={self.store!r}"
            ")"
        )


__all__ = [
    "ExecutionEventEmitter",
]