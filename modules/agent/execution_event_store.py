"""
Ultron Agent Execution Event Store.

v0.44 — Agent Execution Observability
"""

from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Final

from .execution_event import ExecutionEvent


_CLEAR_ALL: Final = object()


class ExecutionEventStore:
    """
    Thread-safe in-memory store for agent execution events.

    Events are grouped by execution ID and preserved in insertion order.
    """

    def __init__(self) -> None:
        self._events: dict[str, list[ExecutionEvent]] = defaultdict(list)
        self._lock = RLock()

    def record(self, event: ExecutionEvent) -> ExecutionEvent:
        """Record and return an execution event."""

        if not isinstance(event, ExecutionEvent):
            raise TypeError("event must be an ExecutionEvent")

        with self._lock:
            self._events[event.execution_id].append(event)

        return event

    def record_many(
        self,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        """Record multiple events atomically."""

        if not isinstance(events, list):
            raise TypeError("events must be a list")

        for event in events:
            if not isinstance(event, ExecutionEvent):
                raise TypeError(
                    "all events must be ExecutionEvent instances"
                )

        with self._lock:
            for event in events:
                self._events[event.execution_id].append(event)

        return list(events)

    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """Return all events for an execution."""

        self._validate_execution_id(execution_id)

        with self._lock:
            return list(self._events.get(execution_id, []))

    def get_latest(
        self,
        execution_id: str,
    ) -> ExecutionEvent | None:
        """Return the latest event for an execution."""

        events = self.get_events(execution_id)

        if not events:
            return None

        return events[-1]

    def get_step_events(
        self,
        execution_id: str,
        step_id: str,
    ) -> list[ExecutionEvent]:
        """Return all events associated with a specific step."""

        self._validate_execution_id(execution_id)

        if not isinstance(step_id, str):
            raise TypeError("step_id must be a string")

        if not step_id.strip():
            raise ValueError("step_id cannot be empty")

        with self._lock:
            return [
                event
                for event in self._events.get(execution_id, [])
                if event.step_id == step_id
            ]

    def count(self, execution_id: str) -> int:
        """Return the number of events for an execution."""

        return len(self.get_events(execution_id))

    def has_events(self, execution_id: str) -> bool:
        """Return whether an execution has any recorded events."""

        return self.count(execution_id) > 0

    def execution_ids(self) -> list[str]:
        """Return all execution IDs currently stored."""

        with self._lock:
            return list(self._events.keys())

    def clear(self, execution_id: str | object = _CLEAR_ALL) -> None:
        """
        Clear stored events.

        Calling clear() without an argument clears the entire store.

        Providing an execution ID clears only that execution.

        Explicitly passing None is invalid and raises TypeError.
        """

        if execution_id is _CLEAR_ALL:
            with self._lock:
                self._events.clear()
            return

        self._validate_execution_id(execution_id)

        with self._lock:
            self._events.pop(execution_id, None)

    def snapshot(self) -> dict[str, list[ExecutionEvent]]:
        """Return a defensive snapshot of the complete event store."""

        with self._lock:
            return {
                execution_id: list(events)
                for execution_id, events in self._events.items()
            }

    @staticmethod
    def _validate_execution_id(execution_id: object) -> None:
        """Validate an execution identifier."""

        if not isinstance(execution_id, str):
            raise TypeError("execution_id must be a string")

        if not execution_id.strip():
            raise ValueError("execution_id cannot be empty")


__all__ = ["ExecutionEventStore"]