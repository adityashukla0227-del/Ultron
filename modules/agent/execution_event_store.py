"""
Ultron Agent Execution Event Store.

Thread-safe in-memory storage for structured agent execution events.

v0.44 — Agent Execution Observability
"""

from __future__ import annotations

from threading import RLock
from typing import Final

from .execution_event import ExecutionEvent


_CLEAR_ALL: Final = object()


class ExecutionEventStore:
    """
    Thread-safe in-memory store for agent execution events.

    Events are grouped by execution ID and preserved in insertion order.

    The store provides:
    - Event recording
    - Batch event recording
    - Execution-scoped retrieval
    - Step-scoped retrieval
    - Latest-event lookup
    - Event counting
    - Execution existence checks
    - Selective clearing
    - Complete snapshots
    """

    def __init__(self) -> None:
        self._events: dict[str, list[ExecutionEvent]] = {}
        self._lock = RLock()

    # ========================================================
    # Record
    # ========================================================

    def record(
        self,
        event: ExecutionEvent,
    ) -> ExecutionEvent:
        """
        Record and return an execution event.

        Events are appended in insertion order.
        """

        self._validate_event(event)

        with self._lock:

            execution_events = self._events.setdefault(
                event.execution_id,
                [],
            )

            execution_events.append(
                event
            )

        return event

    # ========================================================
    # Record Many
    # ========================================================

    def record_many(
        self,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        """
        Record multiple events atomically.

        Validation is completed for the entire batch before
        any event is stored.
        """

        if not isinstance(
            events,
            list,
        ):
            raise TypeError(
                "events must be a list"
            )

        for event in events:
            self._validate_event(
                event
            )

        with self._lock:

            for event in events:

                execution_events = self._events.setdefault(
                    event.execution_id,
                    [],
                )

                execution_events.append(
                    event
                )

        return list(events)

    # ========================================================
    # Get Events
    # ========================================================

    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return all events for an execution.

        A new list is returned so callers cannot mutate
        the internal store.
        """

        self._validate_execution_id(
            execution_id
        )

        with self._lock:

            events = self._events.get(
                execution_id
            )

            if events is None:
                return []

            return list(events)

    # ========================================================
    # Latest Event
    # ========================================================

    def get_latest(
        self,
        execution_id: str,
    ) -> ExecutionEvent | None:
        """
        Return the latest event for an execution.

        Returns None when no events exist.
        """

        self._validate_execution_id(
            execution_id
        )

        with self._lock:

            events = self._events.get(
                execution_id
            )

            if not events:
                return None

            return events[-1]

    # ========================================================
    # Step Events
    # ========================================================

    def get_step_events(
        self,
        execution_id: str,
        step_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return all events associated with a specific step.
        """

        self._validate_execution_id(
            execution_id
        )

        self._validate_step_id(
            step_id
        )

        with self._lock:

            events = self._events.get(
                execution_id,
                [],
            )

            return [
                event
                for event in events
                if event.step_id == step_id
            ]

    # ========================================================
    # Count
    # ========================================================

    def count(
        self,
        execution_id: str,
    ) -> int:
        """
        Return the number of events for an execution.
        """

        self._validate_execution_id(
            execution_id
        )

        with self._lock:

            events = self._events.get(
                execution_id
            )

            if events is None:
                return 0

            return len(events)

    # ========================================================
    # Has Events
    # ========================================================

    def has_events(
        self,
        execution_id: str,
    ) -> bool:
        """
        Return whether an execution has recorded events.
        """

        self._validate_execution_id(
            execution_id
        )

        with self._lock:

            events = self._events.get(
                execution_id
            )

            return bool(events)

    # ========================================================
    # Execution IDs
    # ========================================================

    def execution_ids(self) -> list[str]:
        """
        Return all execution IDs currently stored.

        IDs preserve dictionary insertion order.
        """

        with self._lock:
            return list(
                self._events.keys()
            )

    # ========================================================
    # Clear
    # ========================================================

    def clear(
        self,
        execution_id: str | object = _CLEAR_ALL,
    ) -> None:
        """
        Clear stored events.

        Calling clear() without an argument clears the
        entire store.

        Providing an execution ID clears only that execution.

        Explicitly passing None is invalid.
        """

        if execution_id is _CLEAR_ALL:

            with self._lock:
                self._events.clear()

            return

        self._validate_execution_id(
            execution_id
        )

        with self._lock:

            self._events.pop(
                execution_id,
                None,
            )

    # ========================================================
    # Snapshot
    # ========================================================

    def snapshot(
        self,
    ) -> dict[str, list[ExecutionEvent]]:
        """
        Return a defensive snapshot of the complete event store.

        Both the outer dictionary and inner event lists are copied.
        """

        with self._lock:

            return {
                execution_id: list(events)
                for execution_id, events
                in self._events.items()
            }

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_event(
        event: object,
    ) -> None:
        """
        Validate an event instance.
        """

        if not isinstance(
            event,
            ExecutionEvent,
        ):
            raise TypeError(
                "event must be an ExecutionEvent"
            )

    @staticmethod
    def _validate_execution_id(
        execution_id: object,
    ) -> None:
        """
        Validate an execution identifier.
        """

        if not isinstance(
            execution_id,
            str,
        ):
            raise TypeError(
                "execution_id must be a string"
            )

        if not execution_id.strip():
            raise ValueError(
                "execution_id cannot be empty"
            )

    @staticmethod
    def _validate_step_id(
        step_id: object,
    ) -> None:
        """
        Validate a step identifier.
        """

        if not isinstance(
            step_id,
            str,
        ):
            raise TypeError(
                "step_id must be a string"
            )

        if not step_id.strip():
            raise ValueError(
                "step_id cannot be empty"
            )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a concise store representation.
        """

        with self._lock:

            execution_count = len(
                self._events
            )

            event_count = sum(
                len(events)
                for events in self._events.values()
            )

        return (
            "ExecutionEventStore("
            f"executions={execution_count}, "
            f"events={event_count}"
            ")"
        )


__all__ = [
    "ExecutionEventStore",
]