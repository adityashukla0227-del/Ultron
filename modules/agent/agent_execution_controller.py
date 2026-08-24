"""
Ultron Agent Execution Controller
Version: v0.44

Execution control layer for Ultron AI Agents.

Responsibilities:
- Track execution state
- Pause execution
- Resume execution
- Cancel execution
- Retry failed steps
- Skip pending steps
- Enforce retry limits
- Track execution metadata
- Track execution identity
- Emit structured execution events
- Provide execution observability
- Maintain backward-compatible execution history

The AgentExecutionController does NOT create plans.
Planning belongs to AgentPlanner.

The AgentExecutionController does NOT directly execute tools.
Execution belongs to AgentOrchestrator / AgentEngine.

v0.44 — Agent Execution Observability
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from modules.agent.agent import Agent
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanStep,
)
from modules.agent.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)
from modules.agent.execution_event_store import ExecutionEventStore


class AgentExecutionControllerError(Exception):
    """Base exception for execution controller errors."""


class AgentExecutionController:
    """
    Controls the lifecycle of an AgentPlan execution.

    Architecture:

        AgentPlan
            |
            v
        ExecutionController
            |
            +----------------------+
            |                      |
            v                      v
        Execution History     ExecutionEventStore
            |                      |
            |                      v
            |                ExecutionEvent
            |                      |
            +----------+-----------+
                       |
                       v
                AgentOrchestrator
                       |
                       v
                  AgentEngine
    """

    VALID_STATES = {
        "idle",
        "running",
        "paused",
        "cancelled",
        "completed",
        "failed",
    }

    EVENT_TYPE_MAP = {
        "execution_started": ExecutionEventType.EXECUTION_STARTED,
        "execution_completed": ExecutionEventType.EXECUTION_COMPLETED,
        "execution_failed": ExecutionEventType.EXECUTION_FAILED,
        "execution_paused": ExecutionEventType.EXECUTION_PAUSED,
        "execution_resumed": ExecutionEventType.EXECUTION_RESUMED,
        "execution_cancelled": ExecutionEventType.EXECUTION_CANCELLED,
        "step_started": ExecutionEventType.STEP_STARTED,
        "step_completed": ExecutionEventType.STEP_COMPLETED,
        "step_failed": ExecutionEventType.STEP_FAILED,
        "step_retry": ExecutionEventType.STEP_RETRIED,
        "step_skipped": ExecutionEventType.STEP_SKIPPED,
    }

    def __init__(
        self,
        max_retries: int = 3,
        event_store: Optional[ExecutionEventStore] = None,
    ) -> None:
        """
        Initialize the execution controller.

        Args:
            max_retries:
                Maximum number of retries allowed per step.

            event_store:
                Optional ExecutionEventStore instance.

                When supplied, the controller uses the provided
                store. Otherwise, a new in-memory store is created.
        """

        if not isinstance(max_retries, int):
            raise AgentExecutionControllerError(
                "Max retries must be an integer."
            )

        if max_retries < 0:
            raise AgentExecutionControllerError(
                "Max retries cannot be negative."
            )

        if event_store is not None and not isinstance(
            event_store,
            ExecutionEventStore,
        ):
            raise AgentExecutionControllerError(
                "event_store must be an ExecutionEventStore instance."
            )

        self.max_retries = max_retries

        self.state = "idle"

        self.current_plan_id: Optional[str] = None

        self.current_agent_id: Optional[str] = None

        self.current_step_id: Optional[str] = None

        self.execution_id: Optional[str] = None

        self.retry_counts: Dict[str, int] = {}

        # Backward-compatible dictionary history.
        self.execution_history = []

        # Structured observability store.
        self.event_store = (
            event_store
            if event_store is not None
            else ExecutionEventStore()
        )

    # ========================================================
    # Validation
    # ========================================================

    def validate_plan(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> bool:
        """
        Validate the supplied plan and agent.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlan objects are supported."
            )

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentExecutionControllerError(
                "Only Agent instances are supported."
            )

        if plan.agent_id != agent.id:
            raise AgentExecutionControllerError(
                "Plan does not belong to the supplied agent."
            )

        return True

    # ========================================================
    # Start
    # ========================================================

    def start(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> bool:
        """
        Start execution control for a plan.

        A new execution identity is created every time an
        execution is started.
        """

        self.validate_plan(
            plan,
            agent,
        )

        if self.state in {
            "running",
            "paused",
        }:
            raise AgentExecutionControllerError(
                "An execution is already active."
            )

        if plan.is_cancelled():
            raise AgentExecutionControllerError(
                "Cannot start a cancelled plan."
            )

        self.current_plan_id = plan.id

        self.current_agent_id = agent.id

        self.current_step_id = None

        self.retry_counts.clear()

        self.execution_history.clear()

        self.execution_id = str(
            uuid.uuid4()
        )

        self.state = "running"

        self._record_event(
            "execution_started"
        )

        return True

    # ========================================================
    # Pause
    # ========================================================

    def pause(self) -> bool:
        """
        Pause the current execution.
        """

        if self.state != "running":
            return False

        self.state = "paused"

        self._record_event(
            "execution_paused"
        )

        return True

    # ========================================================
    # Resume
    # ========================================================

    def resume(self) -> bool:
        """
        Resume a paused execution.
        """

        if self.state != "paused":
            return False

        self.state = "running"

        self._record_event(
            "execution_resumed"
        )

        return True

    # ========================================================
    # Cancel
    # ========================================================

    def cancel(self) -> bool:
        """
        Cancel the current execution.
        """

        if self.state not in {
            "running",
            "paused",
        }:
            return False

        self.state = "cancelled"

        self._record_event(
            "execution_cancelled"
        )

        return True

    # ========================================================
    # Complete
    # ========================================================

    def complete(self) -> bool:
        """
        Mark execution as completed.
        """

        if self.state != "running":
            return False

        self.state = "completed"

        self.current_step_id = None

        self._record_event(
            "execution_completed"
        )

        return True

    # ========================================================
    # Fail
    # ========================================================

    def fail(
        self,
        error: Optional[str] = None,
    ) -> bool:
        """
        Mark execution as failed.
        """

        if self.state not in {
            "running",
            "paused",
        }:
            return False

        self.state = "failed"

        self._record_event(
            "execution_failed",
            error=error,
        )

        return True

    # ========================================================
    # Current Step
    # ========================================================

    def set_current_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Track the currently executing step.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlanStep objects are supported."
            )

        if self.state != "running":
            return False

        self.current_step_id = step.id

        self._record_event(
            "step_started",
            step_id=step.id,
        )

        return True

    def clear_current_step(self) -> bool:
        """
        Clear the current step.
        """

        self.current_step_id = None

        return True

    # ========================================================
    # Retry
    # ========================================================

    def can_retry(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Check whether a failed step can be retried.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlanStep objects are supported."
            )

        attempts = self.retry_counts.get(
            step.id,
            0,
        )

        return attempts < self.max_retries

    def retry_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Retry a failed step.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlanStep objects are supported."
            )

        if not step.is_failed():
            return False

        if not self.can_retry(step):
            return False

        self.retry_counts[step.id] = (
            self.retry_counts.get(
                step.id,
                0,
            )
            + 1
        )

        step.reset()

        self._record_event(
            "step_retry",
            step_id=step.id,
            retry_count=self.retry_counts[
                step.id
            ],
        )

        return True

    # ========================================================
    # Skip
    # ========================================================

    def skip_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Skip a pending step.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlanStep objects are supported."
            )

        if not step.is_pending():
            return False

        step.skip()

        self._record_event(
            "step_skipped",
            step_id=step.id,
        )

        return True

    # ========================================================
    # State Queries
    # ========================================================

    def is_running(self) -> bool:
        return self.state == "running"

    def is_paused(self) -> bool:
        return self.state == "paused"

    def is_cancelled(self) -> bool:
        return self.state == "cancelled"

    def is_completed(self) -> bool:
        return self.state == "completed"

    def is_failed(self) -> bool:
        return self.state == "failed"

    def is_active(self) -> bool:
        return self.state in {
            "running",
            "paused",
        }

    # ========================================================
    # Retry Information
    # ========================================================

    def get_retry_count(
        self,
        step: AgentPlanStep,
    ) -> int:
        """
        Return retry count for a step.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentExecutionControllerError(
                "Only AgentPlanStep objects are supported."
            )

        return self.retry_counts.get(
            step.id,
            0,
        )

    # ========================================================
    # History
    # ========================================================

    def _record_event(
        self,
        event: str,
        **metadata: Any,
    ) -> None:
        """
        Record an execution event.

        Two representations are maintained:

        1. Legacy dictionary history for backward compatibility.
        2. Structured ExecutionEvent for observability.
        """

        if not isinstance(event, str):
            raise AgentExecutionControllerError(
                "event must be a string."
            )

        event_type = self.EVENT_TYPE_MAP.get(
            event
        )

        if event_type is None:
            raise AgentExecutionControllerError(
                f"Unsupported execution event type: {event}"
            )

        step_id = metadata.get(
            "step_id",
            self.current_step_id,
        )

        # Ensure an execution identity exists before emitting
        # any structured event.
        if self.execution_id is None:
            self.execution_id = str(
                uuid.uuid4()
            )

        # ----------------------------------------------------
        # Backward-compatible history
        # ----------------------------------------------------

        history_entry = {
            "event": event,
            "plan_id": self.current_plan_id,
            "agent_id": self.current_agent_id,
            "step_id": self.current_step_id,
            **metadata,
        }

        self.execution_history.append(
            history_entry
        )

        # ----------------------------------------------------
        # Structured event
        # ----------------------------------------------------

        event_metadata = dict(
            metadata
        )

        event_metadata.setdefault(
            "plan_id",
            self.current_plan_id,
        )

        event_metadata.setdefault(
            "agent_id",
            self.current_agent_id,
        )

        message = event_metadata.pop(
            "message",
            None,
        )

        execution_event = ExecutionEvent(
            event_type=event_type,
            execution_id=self.execution_id,
            step_id=step_id,
            message=message,
            metadata=event_metadata,
        )

        self.event_store.record(
            execution_event
        )

    def get_history(self):
        """
        Return execution history.

        This method remains backward-compatible with v0.43.
        """

        return list(
            self.execution_history
        )

    # ========================================================
    # Structured Event Observability
    # ========================================================

    def get_events(self) -> list[ExecutionEvent]:
        """
        Return all structured events for the current execution.
        """

        if self.execution_id is None:
            return []

        return self.event_store.get_events(
            self.execution_id
        )

    def get_latest_event(
        self,
    ) -> Optional[ExecutionEvent]:
        """
        Return the latest structured event for the current execution.
        """

        if self.execution_id is None:
            return None

        return self.event_store.get_latest(
            self.execution_id
        )

    def get_event_count(self) -> int:
        """
        Return the number of structured events for the current execution.
        """

        if self.execution_id is None:
            return 0

        return self.event_store.count(
            self.execution_id
        )

    def get_step_events(
        self,
        step_id: str,
    ) -> list[ExecutionEvent]:
        """
        Return structured events associated with a step.
        """

        if self.execution_id is None:
            return []

        return self.event_store.get_step_events(
            self.execution_id,
            step_id,
        )

    def get_execution_id(self) -> Optional[str]:
        """
        Return the current execution ID.
        """

        return self.execution_id

    # ========================================================
    # Status
    # ========================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Return complete controller status.
        """

        return {
            "state": self.state,
            "execution_id": self.execution_id,
            "plan_id": self.current_plan_id,
            "agent_id": self.current_agent_id,
            "current_step_id": self.current_step_id,
            "max_retries": self.max_retries,
            "retry_counts": dict(
                self.retry_counts
            ),
            "history_size": len(
                self.execution_history
            ),
            "event_count": self.get_event_count(),
        }

    # ========================================================
    # Reset
    # ========================================================

    def reset(self) -> bool:
        """
        Reset the execution controller.

        Structured events belonging to the current execution
        are removed from the controller's in-memory event store.
        """

        if self.execution_id is not None:
            self.event_store.clear(
                self.execution_id
            )

        self.state = "idle"

        self.current_plan_id = None

        self.current_agent_id = None

        self.current_step_id = None

        self.execution_id = None

        self.retry_counts.clear()

        self.execution_history.clear()

        return True

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "AgentExecutionController("
            f"state='{self.state}', "
            f"max_retries={self.max_retries}, "
            f"execution_id='{self.execution_id}'"
            ")"
        )


__all__ = [
    "AgentExecutionController",
    "AgentExecutionControllerError",
]