"""
Ultron Agent Orchestrator
Version: v0.50

Execution orchestration layer for Ultron AI Agents.

v0.50 additions:
- ExecutionContext integration
- Centralized execution runtime state
- Step result tracking
- Step failure tracking
- Retry tracking
- Skip tracking
- Lifecycle synchronization
- Execution context snapshots
- Context-aware progress validation
- Defensive result/state consistency
- Terminal-state hardening
- Safe context/controller synchronization

Responsibilities:
- Validate execution plans
- Start plan execution
- Integrate AgentExecutionController
- Integrate ExecutionContext
- Integrate ExecutionEventEmitter
- Execute plan steps sequentially
- Resolve step tools through AgentEngine
- Record step results
- Handle step failures safely
- Track plan progress
- Track execution state
- Support pause / resume / cancel
- Support retry and skip through controller
- Emit structured execution events
- Complete or fail plans
- Provide safe plan execution

The AgentOrchestrator does NOT create plans.
Planning belongs to AgentPlanner.

The AgentOrchestrator does NOT directly execute tools.
Tool execution belongs to AgentEngine.

Execution lifecycle control belongs to
AgentExecutionController.

Execution runtime state belongs to
ExecutionContext.

Execution observability belongs to
ExecutionEventEmitter.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.agent_execution_controller import (
    AgentExecutionController,
    AgentExecutionControllerError,
)
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanStep,
    AgentPlanner,
)
from modules.agent.execution_context import (
    ExecutionContext,
    ExecutionContextError,
)
from modules.agent.execution_event_emitter import (
    ExecutionEventEmitter,
)
from modules.agent.tool_result import ToolResult


class AgentOrchestratorError(Exception):
    """Base exception for agent orchestration errors."""


class AgentOrchestrator:
    """
    Orchestrates sequential execution of AgentPlan steps.

    The orchestrator coordinates:
        AgentPlan
            |
            v
        AgentOrchestrator
            |
            +----------------------+----------------------+------------------+
            |                      |                      |
            v                      v                      v
    ExecutionController      ExecutionContext      EventEmitter
            |                      |                      |
            v                      v                      v
       AgentEngine            Runtime State       Observability
            |
            v
       ToolSelector
            |
            v
       ToolRegistry
    """

    def __init__(
        self,
        engine: Optional[AgentEngine] = None,
        planner: Optional[AgentPlanner] = None,
        controller: Optional[AgentExecutionController] = None,
        emitter: Optional[ExecutionEventEmitter] = None,
        context: Optional[ExecutionContext] = None,
    ) -> None:
        """Initialize the agent orchestrator."""

        self.engine = (
            engine
            if engine is not None
            else AgentEngine()
        )

        self.planner = (
            planner
            if planner is not None
            else AgentPlanner()
        )

        self.controller = (
            controller
            if controller is not None
            else AgentExecutionController()
        )

        self.emitter = (
            emitter
            if emitter is not None
            else ExecutionEventEmitter()
        )

        self.context = context

    # ========================================================
    # Internal Defensive Helpers
    # ========================================================

    @staticmethod
    def _safe_error_message(
        exc: BaseException,
        fallback: str,
    ) -> str:
        """Return a stable non-empty error message."""

        try:
            message = str(exc).strip()
        except Exception:
            message = ""

        return message or fallback

    def _safe_context_operation(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        Execute a context mutation defensively.

        Context bookkeeping must never corrupt or interrupt the
        primary orchestration path.
        """

        context = self.context

        if context is None:
            return False

        try:
            method = getattr(
                context,
                method_name,
            )
        except AttributeError:
            return False

        try:
            method(
                *args,
                **kwargs,
            )
            return True
        except (
            ExecutionContextError,
            AttributeError,
            TypeError,
            ValueError,
        ):
            return False

    def _safe_controller_operation(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Execute a controller mutation without leaking controller errors."""

        try:
            method = getattr(
                self.controller,
                method_name,
            )
        except AttributeError:
            return False

        try:
            method(
                *args,
                **kwargs,
            )
            return True
        except (
            AgentExecutionControllerError,
            AttributeError,
            TypeError,
            ValueError,
        ):
            return False

    @staticmethod
    def _result_is_success(
        result: Any,
    ) -> bool:
        """Return True only for a valid successful ToolResult."""

        return (
            isinstance(result, ToolResult)
            and bool(result.success)
        )

    @staticmethod
    def _result_error(
        result: ToolResult,
        fallback: str = "Tool execution failed.",
    ) -> str:
        """Extract a stable error message from a failed ToolResult."""

        error = getattr(
            result,
            "error",
            None,
        )

        if error is None:
            return fallback

        try:
            error_text = str(error).strip()
        except Exception:
            error_text = ""

        return error_text or fallback

    def _clear_current_step_safely(self) -> None:
        """Clear controller current-step state safely."""

        if self.controller.is_running():
            self._safe_controller_operation(
                "clear_current_step",
            )

    def _fail_plan_safely(
        self,
        plan: AgentPlan,
    ) -> None:
        """Fail a plan without masking the original error."""

        try:
            if not plan.is_failed():
                plan.fail()
        except Exception:
            pass

    def _fail_controller_safely(
        self,
        error: str,
    ) -> None:
        """Fail the controller without masking the original error."""

        try:
            if self.controller.is_active():
                self.controller.fail(error)
        except Exception:
            pass

    def _terminal_result(
        self,
        plan: AgentPlan,
        agent: Agent,
        *,
        success: bool,
        error: str | None,
    ) -> Dict[str, Any]:
        """
        Build a consistent terminal execution result.

        Keeping result construction centralized prevents subtle
        differences between failure paths.
        """

        return {
            "success": bool(success),
            "plan_id": getattr(
                plan,
                "id",
                None,
            ),
            "agent_id": getattr(
                agent,
                "id",
                None,
            ),
            "result": None,
            "error": error,
            "progress": self.planner.get_progress(plan),
        }

    # ========================================================
    # Execution Context
    # ========================================================

    def _create_execution_context(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> ExecutionContext:
        """
        Create or reuse the execution context for this execution.
        """

        execution_id = self._execution_id(plan)

        if (
            isinstance(self.context, ExecutionContext)
            and self.context.execution_id == execution_id
        ):
            return self.context

        self.context = ExecutionContext(
            execution_id,
            plan_id=str(plan.id),
            agent_id=str(agent.id),
        )

        return self.context

    def _context(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> ExecutionContext:
        """Return the active execution context."""

        return self._create_execution_context(
            plan,
            agent,
        )

    def get_execution_context(
        self,
    ) -> ExecutionContext | None:
        """Return the current execution context."""

        return self.context

    def get_context_snapshot(
        self,
    ) -> Dict[str, Any] | None:
        """Return a defensive snapshot of the current context."""

        if self.context is None:
            return None

        try:
            snapshot = self.context.snapshot()
        except (
            ExecutionContextError,
            AttributeError,
            TypeError,
            ValueError,
        ):
            return None

        if isinstance(snapshot, dict):
            return dict(snapshot)

        return snapshot

    def _context_start(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> None:
        """Start and initialize execution context."""

        context = self._context(
            plan,
            agent,
        )

        try:
            context.set_total_steps(
                len(plan.steps)
            )
            context.start()
        except ExecutionContextError as exc:
            raise AgentOrchestratorError(
                f"Unable to start execution context: {exc}"
            ) from exc

    def _context_pause(self) -> None:
        """Pause the active execution context."""

        if self.context is None:
            return

        try:
            if self.context.is_running():
                self.context.pause()
        except ExecutionContextError:
            pass

    def _context_resume(self) -> None:
        """Resume the active execution context."""

        if self.context is None:
            return

        try:
            if self.context.is_paused():
                self.context.resume()
        except ExecutionContextError:
            pass

    def _context_cancel(self) -> None:
        """Cancel the active execution context."""

        if self.context is None:
            return

        try:
            if not self.context.is_cancelled():
                self.context.cancel()
        except ExecutionContextError:
            pass

    def _context_fail(self) -> None:
        """Fail the active execution context."""

        if self.context is None:
            return

        try:
            if not self.context.is_failed():
                self.context.fail()
        except ExecutionContextError:
            pass

    def _context_complete(self) -> None:
        """Complete the active execution context."""

        if self.context is None:
            return

        try:
            if not self.context.is_completed():
                self.context.complete()
        except ExecutionContextError:
            pass

    def _record_context_completed_step(
        self,
        step: AgentPlanStep,
        result: Any,
    ) -> None:
        """Record successful step completion safely."""

        self._safe_context_operation(
            "record_completed_step",
            step.id,
            result,
        )

    def _record_context_failed_step(
        self,
        step: AgentPlanStep,
        error: str,
    ) -> None:
        """Record step failure safely."""

        self._safe_context_operation(
            "record_failed_step",
            step.id,
            error,
        )

    def _record_context_retried_step(
        self,
        step: AgentPlanStep,
    ) -> None:
        """Record step retry safely."""

        self._safe_context_operation(
            "record_retried_step",
            step.id,
        )

    def _record_context_skipped_step(
        self,
        step: AgentPlanStep,
    ) -> None:
        """Record step skip safely."""

        self._safe_context_operation(
            "record_skipped_step",
            step.id,
        )

    def _set_context_current_step(
        self,
        step: AgentPlanStep,
    ) -> None:
        """Update context current-step information safely."""

        if self.context is None:
            return

        self._safe_context_operation(
            "set_current_step",
            step.id,
            step_index=self._step_index(step),
        )

    def _validate_context_progress(
        self,
        *,
        expected_total_steps: int | None = None,
    ) -> bool:
        """
        Validate execution-context progress consistency.

        Validation is deliberately non-fatal. Context is a runtime
        analytics/state layer and must not corrupt the primary plan
        execution path.
        """

        context = self.context

        if context is None:
            return True

        try:
            total_steps = context.total_steps
            processed_steps = context.get_processed_steps()
            remaining_steps = context.get_remaining_steps()

            if not isinstance(total_steps, int):
                return False

            if not isinstance(processed_steps, int):
                return False

            if not isinstance(remaining_steps, int):
                return False

            if total_steps < 0:
                return False

            if processed_steps < 0:
                return False

            if remaining_steps < 0:
                return False

            if processed_steps > total_steps:
                return False

            if (
                expected_total_steps is not None
                and total_steps != expected_total_steps
            ):
                return False

            expected_remaining = max(
                total_steps - processed_steps,
                0,
            )

            if remaining_steps != expected_remaining:
                return False

            return True

        except (
            AttributeError,
            TypeError,
            ValueError,
            ExecutionContextError,
        ):
            return False

    def _synchronize_context_progress(
        self,
        plan: AgentPlan,
    ) -> bool:
        """
        Validate active context against the current plan.

        Returns the validation state for diagnostics, while keeping
        synchronization non-fatal.
        """

        if self.context is None:
            return True

        return self._validate_context_progress(
            expected_total_steps=len(plan.steps),
        )

    # ========================================================
    # Observability Helpers
    # ========================================================

    @staticmethod
    def _execution_id(
        plan: AgentPlan,
    ) -> str:
        """Return the stable execution identifier for a plan."""

        return str(plan.id)

    @staticmethod
    def _step_index(
        step: AgentPlanStep,
    ) -> int | None:
        """Return a step index when available."""

        value = getattr(
            step,
            "step_index",
            None,
        )

        if value is None:
            value = getattr(
                step,
                "index",
                None,
            )

        if isinstance(value, int):
            return value

        return None

    def _emit(
        self,
        method_name: str,
        execution_id: str,
        *,
        step: AgentPlanStep | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Safely emit an execution event."""

        try:
            method = getattr(
                self.emitter,
                method_name,
            )

            kwargs: dict[str, Any] = {}

            if step is not None:
                kwargs["step_id"] = step.id

                step_index = self._step_index(step)

                if step_index is not None:
                    kwargs["step_index"] = step_index

            if message is not None:
                kwargs["message"] = message

            if metadata is not None:
                kwargs["metadata"] = dict(metadata)

            method(
                execution_id,
                **kwargs,
            )

        except Exception:
            pass

    def _emit_execution_started(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> None:
        """Emit an execution_started event."""

        self._emit(
            "execution_started",
            self._execution_id(plan),
            message="Agent plan execution started.",
            metadata={
                "plan_id": plan.id,
                "agent_id": agent.id,
            },
        )

    def _emit_execution_completed(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> None:
        """Emit an execution_completed event."""

        self._emit(
            "execution_completed",
            self._execution_id(plan),
            message="Agent plan execution completed.",
            metadata={
                "plan_id": plan.id,
                "agent_id": agent.id,
            },
        )

    def _emit_execution_failed(
        self,
        plan: AgentPlan,
        agent: Agent,
        error: str,
    ) -> None:
        """Emit an execution_failed event."""

        self._emit(
            "execution_failed",
            self._execution_id(plan),
            message=error,
            metadata={
                "plan_id": plan.id,
                "agent_id": agent.id,
                "error": error,
            },
        )

    def _emit_execution_paused(
        self,
        plan: AgentPlan | None,
    ) -> None:
        """Emit an execution_paused event."""

        if not isinstance(plan, AgentPlan):
            return

        self._emit(
            "execution_paused",
            self._execution_id(plan),
            message="Agent plan execution paused.",
            metadata={
                "plan_id": plan.id,
            },
        )

    def _emit_execution_resumed(
        self,
        plan: AgentPlan | None,
    ) -> None:
        """Emit an execution_resumed event."""

        if not isinstance(plan, AgentPlan):
            return

        self._emit(
            "execution_resumed",
            self._execution_id(plan),
            message="Agent plan execution resumed.",
            metadata={
                "plan_id": plan.id,
            },
        )

    def _emit_execution_cancelled(
        self,
        plan: AgentPlan | None,
    ) -> None:
        """Emit an execution_cancelled event."""

        if not isinstance(plan, AgentPlan):
            return

        self._emit(
            "execution_cancelled",
            self._execution_id(plan),
            message="Agent plan execution cancelled.",
            metadata={
                "plan_id": plan.id,
            },
        )

    def _emit_step_started(
        self,
        plan: AgentPlan,
        step: AgentPlanStep,
    ) -> None:
        """Emit a step_started event."""

        self._emit(
            "step_started",
            self._execution_id(plan),
            step=step,
            message=f"Step '{step.id}' started.",
            metadata={
                "step_id": step.id,
                "tool_name": step.tool_name,
            },
        )

    def _emit_step_completed(
        self,
        plan: AgentPlan,
        step: AgentPlanStep,
    ) -> None:
        """Emit a step_completed event."""

        self._emit(
            "step_completed",
            self._execution_id(plan),
            step=step,
            message=f"Step '{step.id}' completed.",
            metadata={
                "step_id": step.id,
                "tool_name": step.tool_name,
            },
        )

    def _emit_step_failed(
        self,
        plan: AgentPlan,
        step: AgentPlanStep,
        error: str,
    ) -> None:
        """Emit a step_failed event."""

        self._emit(
            "step_failed",
            self._execution_id(plan),
            step=step,
            message=error,
            metadata={
                "step_id": step.id,
                "tool_name": step.tool_name,
                "error": error,
            },
        )

    def _emit_step_retried(
        self,
        plan: AgentPlan | None,
        step: AgentPlanStep,
    ) -> None:
        """Emit a step_retried event."""

        if not isinstance(plan, AgentPlan):
            return

        self._emit(
            "step_retried",
            self._execution_id(plan),
            step=step,
            message=f"Step '{step.id}' retried.",
            metadata={
                "step_id": step.id,
            },
        )

    def _emit_step_skipped(
        self,
        plan: AgentPlan | None,
        step: AgentPlanStep,
    ) -> None:
        """Emit a step_skipped event."""

        if not isinstance(plan, AgentPlan):
            return

        self._emit(
            "step_skipped",
            self._execution_id(plan),
            step=step,
            message=f"Step '{step.id}' skipped.",
            metadata={
                "step_id": step.id,
            },
        )

    # ========================================================
    # Validation
    # ========================================================

    def validate_plan(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> bool:
        """Validate that a plan is executable by the supplied agent."""

        if not isinstance(plan, AgentPlan):
            raise AgentOrchestratorError(
                "Only AgentPlan objects can be orchestrated."
            )

        if not isinstance(agent, Agent):
            raise AgentOrchestratorError(
                "Only Agent instances can execute plans."
            )

        try:
            self.planner.validate_plan(
                plan,
                agent=agent,
            )
        except Exception as exc:
            raise AgentOrchestratorError(
                f"Plan validation failed: {exc}"
            ) from exc

        if plan.is_empty():
            raise AgentOrchestratorError(
                "Cannot execute an empty plan."
            )

        if plan.is_cancelled():
            raise AgentOrchestratorError(
                "Cannot execute a cancelled plan."
            )

        return True

    # ========================================================
    # Step Resolution
    # ========================================================

    def get_next_step(
        self,
        plan: AgentPlan,
    ) -> Optional[AgentPlanStep]:
        """Return the next pending step in the plan."""

        if not isinstance(plan, AgentPlan):
            raise AgentOrchestratorError(
                "Only AgentPlan objects are supported."
            )

        return self.planner.get_next_step(plan)

    # ========================================================
    # Step Execution
    # ========================================================

    def execute_step(
        self,
        agent: Agent,
        step: AgentPlanStep,
        *,
        plan: AgentPlan | None = None,
    ) -> Any:
        """
        Execute a single plan step.

        Tool execution is delegated to AgentEngine.
        """

        if not isinstance(agent, Agent):
            raise AgentOrchestratorError(
                "Only Agent instances can execute steps."
            )

        if not isinstance(step, AgentPlanStep):
            raise AgentOrchestratorError(
                "Only AgentPlanStep objects can be executed."
            )

        if step.is_finished():
            raise AgentOrchestratorError(
                f"Step is already finished: {step.id}"
            )

        if not step.tool_name:
            raise AgentOrchestratorError(
                f"Step '{step.id}' has no tool assigned."
            )

        observability_plan = (
            plan
            if isinstance(plan, AgentPlan)
            else None
        )

        # ----------------------------------------------------
        # Context Current Step
        # ----------------------------------------------------

        if observability_plan is not None:
            self._set_context_current_step(step)

        # ----------------------------------------------------
        # Controller Current Step
        # ----------------------------------------------------

        if self.controller.is_running():
            try:
                self.controller.set_current_step(step)
            except AgentExecutionControllerError as exc:
                raise AgentOrchestratorError(
                    f"Unable to track execution step: {exc}"
                ) from exc

        # ----------------------------------------------------
        # Start Step
        # ----------------------------------------------------

        try:
            step.start()
        except Exception as exc:
            error = self._safe_error_message(
                exc,
                f"Unable to start step '{step.id}'.",
            )

            self._record_context_failed_step(
                step,
                error,
            )

            if observability_plan is not None:
                self._emit_step_failed(
                    observability_plan,
                    step,
                    error,
                )

            self._clear_current_step_safely()

            raise AgentOrchestratorError(
                error
            ) from exc

        if observability_plan is not None:
            self._emit_step_started(
                observability_plan,
                step,
            )

        # ----------------------------------------------------
        # Execute Tool
        # ----------------------------------------------------

        try:
            result = self.engine.execute_tool_safe(
                agent,
                step.tool_name,
                **step.parameters,
            )

        except Exception as exc:
            error = self._safe_error_message(
                exc,
                "Tool execution failed.",
            )

            try:
                step.fail(error)
            except Exception:
                pass

            self._record_context_failed_step(
                step,
                error,
            )

            if observability_plan is not None:
                self._emit_step_failed(
                    observability_plan,
                    step,
                    error,
                )

                self._synchronize_context_progress(
                    observability_plan,
                )

            self._clear_current_step_safely()

            raise AgentOrchestratorError(
                f"Step '{step.id}' execution failed: {error}"
            ) from exc

        # ----------------------------------------------------
        # Validate Result
        # ----------------------------------------------------

        if not isinstance(result, ToolResult):
            error = (
                "AgentEngine returned an invalid tool result."
            )

            try:
                step.fail(error)
            except Exception:
                pass

            self._record_context_failed_step(
                step,
                error,
            )

            if observability_plan is not None:
                self._emit_step_failed(
                    observability_plan,
                    step,
                    error,
                )

                self._synchronize_context_progress(
                    observability_plan,
                )

            self._clear_current_step_safely()

            raise AgentOrchestratorError(
                f"Invalid tool result for step: {step.id}"
            )

        # ----------------------------------------------------
        # Successful Result
        # ----------------------------------------------------

        if self._result_is_success(result):

            try:
                step.complete(
                    result.result
                )
            except Exception as exc:
                error = self._safe_error_message(
                    exc,
                    f"Unable to complete step '{step.id}'.",
                )

                self._record_context_failed_step(
                    step,
                    error,
                )

                if observability_plan is not None:
                    self._emit_step_failed(
                        observability_plan,
                        step,
                        error,
                    )

                    self._synchronize_context_progress(
                        observability_plan,
                    )

                self._clear_current_step_safely()

                raise AgentOrchestratorError(
                    f"Unable to finalize step '{step.id}': {error}"
                ) from exc

            self._record_context_completed_step(
                step,
                result.result,
            )

            if observability_plan is not None:
                self._emit_step_completed(
                    observability_plan,
                    step,
                )

                self._synchronize_context_progress(
                    observability_plan,
                )

            self._clear_current_step_safely()

            return result

        # ----------------------------------------------------
        # Failed Result
        # ----------------------------------------------------

        error = self._result_error(result)

        try:
            step.fail(error)
        except Exception:
            pass

        self._record_context_failed_step(
            step,
            error,
        )

        if observability_plan is not None:
            self._emit_step_failed(
                observability_plan,
                step,
                error,
            )

            self._synchronize_context_progress(
                observability_plan,
            )

        self._clear_current_step_safely()

        return result

    # ========================================================
    # Plan Execution
    # ========================================================

    def execute_plan(
        self,
        agent: Agent,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """Execute all plan steps sequentially."""

        self.validate_plan(
            plan,
            agent,
        )

        # ----------------------------------------------------
        # Prepare Plan
        # ----------------------------------------------------

        if plan.is_draft():
            try:
                plan.prepare()
            except Exception as exc:
                error = self._safe_error_message(
                    exc,
                    "Unable to prepare plan.",
                )

                self._emit_execution_failed(
                    plan,
                    agent,
                    error,
                )

                raise AgentOrchestratorError(
                    error
                ) from exc

        # ----------------------------------------------------
        # Validate Ready State
        # ----------------------------------------------------

        if not plan.is_ready():
            error = (
                f"Plan is not ready for execution: "
                f"{plan.status}"
            )

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            raise AgentOrchestratorError(error)

        # ----------------------------------------------------
        # Initialize Execution Context
        # ----------------------------------------------------

        try:
            self._context_start(
                plan,
                agent,
            )

            self._synchronize_context_progress(
                plan,
            )

        except AgentOrchestratorError as exc:
            self._emit_execution_failed(
                plan,
                agent,
                str(exc),
            )
            raise

        # ----------------------------------------------------
        # Start Controller
        # ----------------------------------------------------

        try:
            self.controller.start(
                plan,
                agent,
            )
        except AgentExecutionControllerError as exc:
            error = self._safe_error_message(
                exc,
                "Unable to start execution controller.",
            )

            self._context_fail()

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            raise AgentOrchestratorError(
                f"Unable to start execution controller: {error}"
            ) from exc

        # ----------------------------------------------------
        # Start Plan
        # ----------------------------------------------------

        try:
            plan.start()
        except Exception as exc:
            error = self._safe_error_message(
                exc,
                "Unable to start plan.",
            )

            self._context_fail()
            self._fail_controller_safely(error)

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            raise AgentOrchestratorError(
                error
            ) from exc

        # ----------------------------------------------------
        # Start Event
        # ----------------------------------------------------

        self._emit_execution_started(
            plan,
            agent,
        )

        # ----------------------------------------------------
        # Execute Steps
        # ----------------------------------------------------

        while True:

            # ----------------------------------------------
            # Cancellation
            # ----------------------------------------------

            if self.controller.is_cancelled():

                try:
                    if not plan.is_cancelled():
                        plan.cancel()
                except Exception:
                    pass

                self._context_cancel()

                self._emit_execution_cancelled(
                    plan
                )

                return self._terminal_result(
                    plan,
                    agent,
                    success=False,
                    error="Execution was cancelled.",
                )

            # ----------------------------------------------
            # Pause
            # ----------------------------------------------

            if self.controller.is_paused():

                self._context_pause()

                self._emit_execution_paused(
                    plan
                )

                return self._terminal_result(
                    plan,
                    agent,
                    success=False,
                    error="Execution is paused.",
                )

            # ----------------------------------------------
            # Defensive Context Check
            # ----------------------------------------------

            self._synchronize_context_progress(
                plan,
            )

            # ----------------------------------------------
            # Get Next Step
            # ----------------------------------------------

            step = self.get_next_step(plan)

            if step is None:
                break

            # ----------------------------------------------
            # Execute Step
            # ----------------------------------------------

            try:
                result = self.execute_step(
                    agent,
                    step,
                    plan=plan,
                )

            except AgentOrchestratorError as exc:
                error = str(exc) or "Plan step execution failed."

                self._fail_plan_safely(plan)
                self._context_fail()
                self._fail_controller_safely(error)

                self._emit_execution_failed(
                    plan,
                    agent,
                    error,
                )

                return self._terminal_result(
                    plan,
                    agent,
                    success=False,
                    error=error,
                )

            # ----------------------------------------------
            # Step Failure
            # ----------------------------------------------

            if (
                isinstance(result, ToolResult)
                and not result.success
            ):

                error = self._result_error(
                    result,
                    "Plan step execution failed.",
                )

                self._fail_plan_safely(plan)
                self._context_fail()
                self._fail_controller_safely(error)

                self._emit_execution_failed(
                    plan,
                    agent,
                    error,
                )

                return self._terminal_result(
                    plan,
                    agent,
                    success=False,
                    error=error,
                )

            # ----------------------------------------------
            # Step Completion Consistency
            # ----------------------------------------------

            if not step.is_completed():
                error = (
                    f"Step '{step.id}' returned success "
                    "but was not marked complete."
                )

                self._fail_plan_safely(plan)
                self._context_fail()
                self._fail_controller_safely(error)

                self._emit_execution_failed(
                    plan,
                    agent,
                    error,
                )

                return self._terminal_result(
                    plan,
                    agent,
                    success=False,
                    error=error,
                )

            # ----------------------------------------------
            # Context Progress Check
            # ----------------------------------------------

            self._synchronize_context_progress(
                plan,
            )

        # ----------------------------------------------------
        # Verify Completion
        # ----------------------------------------------------

        if not plan.is_complete():

            error = "Plan did not complete successfully."

            self._fail_plan_safely(plan)
            self._context_fail()
            self._fail_controller_safely(error)

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            return self._terminal_result(
                plan,
                agent,
                success=False,
                error=error,
            )

        # ----------------------------------------------------
        # Complete Plan
        # ----------------------------------------------------

        try:
            plan.complete()
        except Exception as exc:
            error = self._safe_error_message(
                exc,
                "Unable to complete plan.",
            )

            self._context_fail()
            self._fail_controller_safely(error)

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            return self._terminal_result(
                plan,
                agent,
                success=False,
                error=error,
            )

        # ----------------------------------------------------
        # Final Context Synchronization
        # ----------------------------------------------------

        self._synchronize_context_progress(
            plan,
        )

        # ----------------------------------------------------
        # Complete Context
        # ----------------------------------------------------

        self._context_complete()

        # ----------------------------------------------------
        # Complete Controller
        # ----------------------------------------------------

        try:
            self.controller.complete()
        except AgentExecutionControllerError as exc:
            error = self._safe_error_message(
                exc,
                "Unable to complete execution controller.",
            )

            # Controller completion failure means the orchestration
            # lifecycle is not fully consistent, even if the plan
            # itself completed.
            self._context_fail()

            self._emit_execution_failed(
                plan,
                agent,
                error,
            )

            return self._terminal_result(
                plan,
                agent,
                success=False,
                error=(
                    "Unable to complete execution controller: "
                    f"{error}"
                ),
            )

        # ----------------------------------------------------
        # Final Completion Event
        # ----------------------------------------------------

        self._emit_execution_completed(
            plan,
            agent,
        )

        return {
            "success": True,
            "plan_id": plan.id,
            "agent_id": agent.id,
            "result": [
                step.result
                for step in plan.completed_steps()
            ],
            "error": None,
            "progress": self.planner.get_progress(plan),
        }

    # ========================================================
    # Safe Plan Execution
    # ========================================================

    def execute_plan_safe(
        self,
        agent: Agent,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """Execute a plan without propagating orchestration errors."""

        try:
            return self.execute_plan(
                agent,
                plan,
            )

        except Exception as exc:

            error = self._safe_error_message(
                exc,
                "Agent plan execution failed.",
            )

            if (
                isinstance(plan, AgentPlan)
                and plan.status
                not in {
                    "completed",
                    "cancelled",
                    "failed",
                }
            ):
                self._fail_plan_safely(plan)

            self._context_fail()

            self._fail_controller_safely(error)

            should_emit_failure = True

            if (
                isinstance(plan, AgentPlan)
                and isinstance(agent, Agent)
            ):
                try:
                    latest_event = self.emitter.get_latest(
                        self._execution_id(plan)
                    )
                except Exception:
                    latest_event = None

                if latest_event is not None:
                    try:
                        event_type = latest_event.event_type.value
                    except AttributeError:
                        event_type = None

                    if event_type == "execution_failed":
                        should_emit_failure = False

            if (
                should_emit_failure
                and isinstance(plan, AgentPlan)
                and isinstance(agent, Agent)
            ):
                self._emit_execution_failed(
                    plan,
                    agent,
                    error,
                )

            return {
                "success": False,
                "plan_id": getattr(
                    plan,
                    "id",
                    None,
                ),
                "agent_id": getattr(
                    agent,
                    "id",
                    None,
                ),
                "result": None,
                "error": error,
                "progress": (
                    self.planner.get_progress(plan)
                    if isinstance(plan, AgentPlan)
                    else None
                ),
            }

    # ========================================================
    # Pause
    # ========================================================

    def pause(self) -> bool:
        """Pause the current execution."""

        try:
            result = self.controller.pause()
        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to pause execution: {exc}"
            ) from exc

        if result:
            self._context_pause()

            controller_plan = getattr(
                self.controller,
                "plan",
                None,
            )

            self._emit_execution_paused(
                controller_plan
            )

        return result

    # ========================================================
    # Resume
    # ========================================================

    def resume(self) -> bool:
        """Resume the current execution."""

        try:
            result = self.controller.resume()
        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to resume execution: {exc}"
            ) from exc

        if result:
            self._context_resume()

            controller_plan = getattr(
                self.controller,
                "plan",
                None,
            )

            self._emit_execution_resumed(
                controller_plan
            )

        return result

    # ========================================================
    # Cancel
    # ========================================================

    def cancel(self) -> bool:
        """Cancel the current execution."""

        try:
            result = self.controller.cancel()
        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to cancel execution: {exc}"
            ) from exc

        if result:
            self._context_cancel()

            controller_plan = getattr(
                self.controller,
                "plan",
                None,
            )

            self._emit_execution_cancelled(
                controller_plan
            )

        return result

    # ========================================================
    # Retry
    # ========================================================

    def retry_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """Retry a failed step through the controller."""

        if not isinstance(step, AgentPlanStep):
            raise AgentOrchestratorError(
                "Only AgentPlanStep objects can be retried."
            )

        try:
            result = self.controller.retry_step(
                step
            )
        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to retry step: {exc}"
            ) from exc

        if result:
            self._record_context_retried_step(
                step
            )

            controller_plan = getattr(
                self.controller,
                "plan",
                None,
            )

            self._emit_step_retried(
                controller_plan,
                step,
            )

            if isinstance(controller_plan, AgentPlan):
                self._synchronize_context_progress(
                    controller_plan,
                )

        return result

    # ========================================================
    # Skip
    # ========================================================

    def skip_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """Skip a pending step through the controller."""

        if not isinstance(step, AgentPlanStep):
            raise AgentOrchestratorError(
                "Only AgentPlanStep objects can be skipped."
            )

        try:
            result = self.controller.skip_step(
                step
            )
        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to skip step: {exc}"
            ) from exc

        if result:
            self._record_context_skipped_step(
                step
            )

            controller_plan = getattr(
                self.controller,
                "plan",
                None,
            )

            self._emit_step_skipped(
                controller_plan,
                step,
            )

            if isinstance(controller_plan, AgentPlan):
                self._synchronize_context_progress(
                    controller_plan,
                )

        return result

    # ========================================================
    # Execution State
    # ========================================================

    def is_running(self) -> bool:
        """Return True when execution is running."""

        return self.controller.is_running()

    def is_paused(self) -> bool:
        """Return True when execution is paused."""

        return self.controller.is_paused()

    def is_cancelled(self) -> bool:
        """Return True when execution is cancelled."""

        return self.controller.is_cancelled()

    def is_completed(self) -> bool:
        """Return True when execution is completed."""

        return self.controller.is_completed()

    def is_failed(self) -> bool:
        """Return True when execution has failed."""

        return self.controller.is_failed()

    def is_active(self) -> bool:
        """Return True when execution is active."""

        return self.controller.is_active()

    # ========================================================
    # Controller Status
    # ========================================================

    def get_execution_status(
        self,
    ) -> Dict[str, Any]:
        """Return execution controller status."""

        return self.controller.get_status()

    # ========================================================
    # Execution History
    # ========================================================

    def get_execution_history(self):
        """Return execution lifecycle history."""

        return self.controller.get_history()

    # ========================================================
    # Execution Events
    # ========================================================

    def get_execution_events(
        self,
        execution_id: str,
    ):
        """Return all observability events for an execution."""

        return self.emitter.get_events(
            execution_id
        )

    def get_latest_execution_event(
        self,
        execution_id: str,
    ):
        """Return the latest observability event."""

        return self.emitter.get_latest(
            execution_id
        )

    def get_step_execution_events(
        self,
        execution_id: str,
        step_id: str,
    ):
        """Return observability events for a specific step."""

        return self.emitter.get_step_events(
            execution_id,
            step_id,
        )

    def get_execution_event_count(
        self,
        execution_id: str,
    ) -> int:
        """Return the number of observability events."""

        return self.emitter.count(
            execution_id
        )

    def clear_execution_events(
        self,
        execution_id: str | object,
    ) -> None:
        """Clear observability events for an execution."""

        self.emitter.clear(
            execution_id
        )

    # ========================================================
    # Progress
    # ========================================================

    def get_progress(
        self,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """Return current execution progress."""

        if not isinstance(plan, AgentPlan):
            raise AgentOrchestratorError(
                "Only AgentPlan objects are supported."
            )

        return self.planner.get_progress(
            plan
        )

    # ========================================================
    # Reset
    # ========================================================

    def reset_execution(self) -> bool:
        """Reset the execution controller and execution context."""

        try:
            result = self.controller.reset()

            self.context = None

            return result

        except AgentExecutionControllerError as exc:
            raise AgentOrchestratorError(
                f"Unable to reset execution: {exc}"
            ) from exc

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "AgentOrchestrator("
            f"engine={self.engine!r}, "
            f"planner={self.planner!r}, "
            f"controller={self.controller!r}, "
            f"emitter={self.emitter!r}, "
            f"context={self.context!r}"
            ")"
        )


__all__ = [
    "AgentOrchestrator",
    "AgentOrchestratorError",
]
