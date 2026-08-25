"""
Ultron Execution Metrics Layer.

v0.46 — Execution Metrics

Provides a dedicated metrics and analytics layer over
ExecutionObservability without coupling metrics logic
to AgentExecutionController or ExecutionEventStore.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.agent.execution_event import ExecutionEventType
from modules.agent.execution_observability import ExecutionObservability


class ExecutionMetricsError(Exception):
    """Base exception for execution metrics errors."""


@dataclass(frozen=True)
class ExecutionMetrics:
    """
    Represents aggregated metrics for a single execution.

    Metrics are derived from structured execution events.
    """

    execution_id: str
    total_events: int
    total_steps: int
    completed_steps: int
    failed_steps: int
    retried_steps: int
    skipped_steps: int
    execution_completed: bool
    execution_failed: bool
    execution_cancelled: bool
    execution_paused: bool
    execution_resumed: bool


class ExecutionMetricsCollector:
    """
    Collects execution metrics from ExecutionObservability.

    Responsibilities:
    - Aggregate execution event counts
    - Calculate step-level metrics
    - Detect execution lifecycle states
    - Provide immutable metric snapshots

    The collector is read-only and does not modify execution
    events, event stores, or controller state.
    """

    def __init__(
        self,
        observability: ExecutionObservability,
    ) -> None:
        """
        Initialize the metrics collector.

        Args:
            observability:
                Existing ExecutionObservability instance.
        """

        if not isinstance(
            observability,
            ExecutionObservability,
        ):
            raise ExecutionMetricsError(
                "observability must be an ExecutionObservability instance."
            )

        self.observability = observability

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
            raise ExecutionMetricsError(
                "execution_id must be a string."
            )

        if not execution_id.strip():
            raise ExecutionMetricsError(
                "execution_id cannot be empty."
            )

    # ========================================================
    # Metrics Collection
    # ========================================================

    def collect(
        self,
        execution_id: str,
    ) -> ExecutionMetrics:
        """
        Collect metrics for a single execution.

        Args:
            execution_id:
                Execution identifier to analyze.

        Returns:
            Immutable ExecutionMetrics snapshot.
        """

        self._validate_execution_id(
            execution_id
        )

        events = self.observability.get_events(
            execution_id
        )

        total_events = len(events)

        step_ids = {
            event.step_id
            for event in events
            if event.step_id is not None
        }

        completed_steps = sum(
            1
            for event in events
            if event.event_type
            == ExecutionEventType.STEP_COMPLETED
        )

        failed_steps = sum(
            1
            for event in events
            if event.event_type
            == ExecutionEventType.STEP_FAILED
        )

        retried_steps = sum(
            1
            for event in events
            if event.event_type
            == ExecutionEventType.STEP_RETRIED
        )

        skipped_steps = sum(
            1
            for event in events
            if event.event_type
            == ExecutionEventType.STEP_SKIPPED
        )

        execution_completed = any(
            event.event_type
            == ExecutionEventType.EXECUTION_COMPLETED
            for event in events
        )

        execution_failed = any(
            event.event_type
            == ExecutionEventType.EXECUTION_FAILED
            for event in events
        )

        execution_cancelled = any(
            event.event_type
            == ExecutionEventType.EXECUTION_CANCELLED
            for event in events
        )

        execution_paused = any(
            event.event_type
            == ExecutionEventType.EXECUTION_PAUSED
            for event in events
        )

        execution_resumed = any(
            event.event_type
            == ExecutionEventType.EXECUTION_RESUMED
            for event in events
        )

        return ExecutionMetrics(
            execution_id=execution_id,
            total_events=total_events,
            total_steps=len(step_ids),
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            retried_steps=retried_steps,
            skipped_steps=skipped_steps,
            execution_completed=execution_completed,
            execution_failed=execution_failed,
            execution_cancelled=execution_cancelled,
            execution_paused=execution_paused,
            execution_resumed=execution_resumed,
        )


__all__ = [
    "ExecutionMetrics",
    "ExecutionMetricsCollector",
    "ExecutionMetricsError",
]