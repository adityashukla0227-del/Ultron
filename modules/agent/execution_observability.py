# modules/agent/execution_observability.py

"""
Ultron Execution Observability Layer.

v0.45 — Execution Observability

Provides a dedicated inspection and query layer over
ExecutionEventStore without coupling observability logic
to AgentExecutionController.
"""

from __future__ import annotations

from typing import Optional

from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_store import ExecutionEventStore


class ExecutionObservabilityError(Exception):
    """Base exception for execution observability errors."""


class ExecutionObservability:
    """
    Provides read-only observability access to execution events.

    Responsibilities:
    - Query execution events
    - Inspect latest events
    - Count execution events
    - Inspect step-specific events
    - Filter events by type and step
    - Inspect execution timelines

    The observability layer does not create, modify, or delete events.
    """

    def __init__(
        self,
        event_store: ExecutionEventStore,
    ) -> None:
        """
        Initialize the observability layer.

        Args:
            event_store:
                Existing ExecutionEventStore instance.
        """

        if not isinstance(
            event_store,
            ExecutionEventStore,
        ):
            raise ExecutionObservabilityError(
                "event_store must be an ExecutionEventStore instance."
            )

        self.event_store = event_store

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_execution_id(
        execution_id: object,
    ) -> None:
        """Validate an execution identifier."""

        if not isinstance(
            execution_id,
            str,
        ):
            raise ExecutionObservabilityError(
                "execution_id must be a string."
            )

        if not execution_id.strip():
            raise ExecutionObservabilityError(
                "execution_id cannot be empty."
            )

    # ========================================================
    # Event Queries
    # ========================================================

    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return all events for an execution.
        """

        self._validate_execution_id(
            execution_id
        )

        return self.event_store.get_events(
            execution_id
        )

    def get_latest_event(
        self,
        execution_id: str,
    ) -> Optional[ExecutionEvent]:
        """
        Return the latest event for an execution.
        """

        self._validate_execution_id(
            execution_id
        )

        return self.event_store.get_latest(
            execution_id
        )

    def get_event_count(
        self,
        execution_id: str,
    ) -> int:
        """
        Return the number of events for an execution.
        """

        self._validate_execution_id(
            execution_id
        )

        return self.event_store.count(
            execution_id
        )

    def get_step_events(
        self,
        execution_id: str,
        step_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return all events associated with a step.
        """

        self._validate_execution_id(
            execution_id
        )

        if not isinstance(
            step_id,
            str,
        ):
            raise ExecutionObservabilityError(
                "step_id must be a string."
            )

        if not step_id.strip():
            raise ExecutionObservabilityError(
                "step_id cannot be empty."
            )

        return self.event_store.get_step_events(
            execution_id,
            step_id,
        )

    def query_events(
        self,
        execution_id: str,
        event_type: ExecutionEventType | None = None,
        step_id: str | None = None,
    ) -> list[ExecutionEvent]:
        """
        Query execution events using optional filters.

        Args:
            execution_id:
                Execution identifier to query.

            event_type:
                Optional event type filter.

            step_id:
                Optional step identifier filter.

        Returns:
            Matching events in their original store order.
        """

        self._validate_execution_id(
            execution_id
        )

        if event_type is not None and not isinstance(
            event_type,
            ExecutionEventType,
        ):
            raise ExecutionObservabilityError(
                "event_type must be an ExecutionEventType or None."
            )

        if step_id is not None:
            if not isinstance(
                step_id,
                str,
            ):
                raise ExecutionObservabilityError(
                    "step_id must be a string or None."
                )

            if not step_id.strip():
                raise ExecutionObservabilityError(
                    "step_id cannot be empty."
                )

        events = self.event_store.get_events(
            execution_id
        )

        if event_type is None and step_id is None:
            return events

        return [
            event
            for event in events
            if (
                event_type is None
                or event.event_type == event_type
            )
            and (
                step_id is None
                or event.step_id == step_id
            )
        ]

    # ========================================================
    # Timeline
    # ========================================================

    def get_timeline(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return execution events in chronological order.

        The underlying event store is not modified.
        """

        self._validate_execution_id(
            execution_id
        )

        events = self.event_store.get_events(
            execution_id
        )

        return sorted(
            events,
            key=lambda event: event.timestamp,
        )


__all__ = [
    "ExecutionObservability",
    "ExecutionObservabilityError",
]