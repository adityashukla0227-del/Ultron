"""
Ultron Agent Orchestrator
Version: v0.43

Execution orchestration layer for Ultron AI Agents.

Responsibilities:
- Validate execution plans
- Start plan execution
- Integrate AgentExecutionController
- Execute plan steps sequentially
- Resolve step tools through AgentEngine
- Record step results
- Handle step failures safely
- Track plan progress
- Track execution state
- Support pause / resume / cancel
- Support retry and skip through controller
- Complete or fail plans
- Provide safe plan execution

The AgentOrchestrator does NOT create plans.
Planning belongs to AgentPlanner.

The AgentOrchestrator does NOT directly execute tools.
Tool execution belongs to AgentEngine.

Execution lifecycle control belongs to
AgentExecutionController.
"""

from typing import Any, Dict, Optional

from modules.agent.agent import Agent
from modules.agent.agent_engine import (
    AgentEngine,
)
from modules.agent.agent_execution_controller import (
    AgentExecutionController,
    AgentExecutionControllerError,
)
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanStep,
    AgentPlanner,
)
from modules.agent.tool_result import ToolResult


class AgentOrchestratorError(Exception):
    """Base exception for agent orchestration errors."""


class AgentOrchestrator:
    """
    Orchestrates sequential execution of AgentPlan steps.

    Architecture:

        AgentPlan
            |
            v
        AgentOrchestrator
            |
            +----------------------+
            |                      |
            v                      v
    ExecutionController       AgentEngine
            |                      |
            |                      v
            |              ToolSelector
            |                      |
            |              ToolRegistry
            |                      |
            |                     Tool
            |
            v
      Execution State

    The orchestrator coordinates execution.

    The controller manages lifecycle state.

    The engine performs actual tool execution.
    """

    def __init__(
        self,
        engine: Optional[AgentEngine] = None,
        planner: Optional[AgentPlanner] = None,
        controller: Optional[AgentExecutionController] = None,
    ) -> None:

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

    # ========================================================
    # Validation
    # ========================================================

    def validate_plan(
        self,
        plan: AgentPlan,
        agent: Agent,
    ) -> bool:
        """
        Validate that a plan belongs to the supplied agent
        and is executable.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentOrchestratorError(
                "Only AgentPlan objects can be orchestrated."
            )

        if not isinstance(
            agent,
            Agent,
        ):
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
        """
        Return the next pending step in the plan.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentOrchestratorError(
                "Only AgentPlan objects are supported."
            )

        return self.planner.get_next_step(
            plan
        )

    # ========================================================
    # Step Execution
    # ========================================================

    def execute_step(
        self,
        agent: Agent,
        step: AgentPlanStep,
    ) -> Any:
        """
        Execute a single plan step.

        Tool-backed steps are delegated to AgentEngine.

        ExecutionController integration is optional for
        direct step execution.

        This preserves backward compatibility with callers
        that execute a single step without starting a complete
        plan execution lifecycle first.

        When execute_step() is called from execute_plan(),
        the controller is already running and tracks the
        current step normally.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentOrchestratorError(
                "Only Agent instances can execute steps."
            )

        if not isinstance(
            step,
            AgentPlanStep,
        ):
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

        # ----------------------------------------------------
        # Controller Integration
        # ----------------------------------------------------
        #
        # If a complete plan execution is active, the
        # controller tracks the current step.
        #
        # For direct execute_step() calls, we intentionally
        # do not require the controller to be running.
        # This preserves the existing public API contract.
        #
        if self.controller.is_running():

            try:

                self.controller.set_current_step(
                    step
                )

            except AgentExecutionControllerError as exc:

                raise AgentOrchestratorError(
                    f"Unable to track execution step: {exc}"
                ) from exc

        # ----------------------------------------------------
        # Start Step
        # ----------------------------------------------------

        step.start()

        # ----------------------------------------------------
        # Execute Through AgentEngine
        # ----------------------------------------------------

        result = self.engine.execute_tool_safe(
            agent,
            step.tool_name,
            **step.parameters,
        )

        # ----------------------------------------------------
        # Validate Result
        # ----------------------------------------------------

        if not isinstance(
            result,
            ToolResult,
        ):

            step.fail(
                "AgentEngine returned an invalid tool result."
            )

            if self.controller.is_running():

                self.controller.clear_current_step()

            raise AgentOrchestratorError(
                f"Invalid tool result for step: {step.id}"
            )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        if result.success:

            step.complete(
                result.result
            )

            if self.controller.is_running():

                self.controller.clear_current_step()

            return result

        # ----------------------------------------------------
        # Failure
        # ----------------------------------------------------

        step.fail(
            result.error
            or "Tool execution failed."
        )

        if self.controller.is_running():

            self.controller.clear_current_step()

        return result

    # ========================================================
    # Plan Execution
    # ========================================================

    def execute_plan(
        self,
        agent: Agent,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """
        Execute all plan steps sequentially.

        The first failed step stops plan execution.

        Execution lifecycle is managed by
        AgentExecutionController.
        """

        self.validate_plan(
            plan,
            agent,
        )

        # ----------------------------------------------------
        # Prepare Draft Plan
        # ----------------------------------------------------

        if plan.is_draft():

            try:

                plan.prepare()

            except Exception as exc:

                raise AgentOrchestratorError(
                    f"Unable to prepare plan: {exc}"
                ) from exc

        # ----------------------------------------------------
        # Validate Ready State
        # ----------------------------------------------------

        if not plan.is_ready():

            raise AgentOrchestratorError(
                f"Plan is not ready for execution: "
                f"{plan.status}"
            )

        # ----------------------------------------------------
        # Start Controller
        # ----------------------------------------------------

        try:

            self.controller.start(
                plan,
                agent,
            )

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to start execution controller: {exc}"
            ) from exc

        # ----------------------------------------------------
        # Start Plan
        # ----------------------------------------------------

        try:

            plan.start()

        except Exception as exc:

            self.controller.fail(
                str(exc)
            )

            raise AgentOrchestratorError(
                f"Unable to start plan: {exc}"
            ) from exc

        # ----------------------------------------------------
        # Execute Steps
        # ----------------------------------------------------

        while True:

            # ----------------------------------------------
            # Cancellation
            # ----------------------------------------------

            if self.controller.is_cancelled():

                try:

                    if not plan.is_finished():

                        plan.cancel()

                except Exception:
                    pass

                return {
                    "success": False,
                    "plan_id": plan.id,
                    "agent_id": agent.id,
                    "result": None,
                    "error": "Execution was cancelled.",
                    "progress": self.planner.get_progress(
                        plan
                    ),
                }

            # ----------------------------------------------
            # Pause Handling
            # ----------------------------------------------
            #
            # execute_plan() is synchronous, so a paused
            # controller cannot continue until resume() is
            # called externally.
            #
            # We return a paused execution result instead
            # of executing another step.
            #
            if self.controller.is_paused():

                return {
                    "success": False,
                    "plan_id": plan.id,
                    "agent_id": agent.id,
                    "result": None,
                    "error": "Execution is paused.",
                    "progress": self.planner.get_progress(
                        plan
                    ),
                }

            # ----------------------------------------------
            # Get Next Step
            # ----------------------------------------------

            step = self.get_next_step(
                plan
            )

            if step is None:

                break

            # ----------------------------------------------
            # Execute Step
            # ----------------------------------------------

            result = self.execute_step(
                agent,
                step,
            )

            # ----------------------------------------------
            # Step Failure
            # ----------------------------------------------

            if (
                isinstance(
                    result,
                    ToolResult,
                )
                and not result.success
            ):

                try:

                    plan.fail()

                finally:

                    self.controller.fail(
                        result.error
                        or "Plan step execution failed."
                    )

                return {
                    "success": False,
                    "plan_id": plan.id,
                    "agent_id": agent.id,
                    "result": None,
                    "error": (
                        result.error
                        or "Plan step execution failed."
                    ),
                    "progress": self.planner.get_progress(
                        plan
                    ),
                }

        # ----------------------------------------------------
        # Verify Plan Completion
        # ----------------------------------------------------

        if not plan.is_complete():

            try:

                plan.fail()

            finally:

                self.controller.fail(
                    "Plan did not complete successfully."
                )

            return {
                "success": False,
                "plan_id": plan.id,
                "agent_id": agent.id,
                "result": None,
                "error": "Plan did not complete successfully.",
                "progress": self.planner.get_progress(
                    plan
                ),
            }

        # ----------------------------------------------------
        # Complete Plan
        # ----------------------------------------------------

        try:

            plan.complete()

        except Exception as exc:

            self.controller.fail(
                str(exc)
            )

            return {
                "success": False,
                "plan_id": plan.id,
                "agent_id": agent.id,
                "result": None,
                "error": f"Unable to complete plan: {exc}",
                "progress": self.planner.get_progress(
                    plan
                ),
            }

        self.controller.complete()

        return {
            "success": True,
            "plan_id": plan.id,
            "agent_id": agent.id,
            "result": [
                step.result
                for step in plan.completed_steps()
            ],
            "error": None,
            "progress": self.planner.get_progress(
                plan
            ),
        }

    # ========================================================
    # Safe Plan Execution
    # ========================================================

    def execute_plan_safe(
        self,
        agent: Agent,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """
        Execute a plan without propagating orchestration errors.
        """

        try:

            return self.execute_plan(
                agent,
                plan,
            )

        except Exception as exc:

            # ----------------------------------------------
            # Fail Plan Safely
            # ----------------------------------------------

            if (
                isinstance(
                    plan,
                    AgentPlan,
                )
                and plan.status
                not in {
                    "completed",
                    "cancelled",
                }
            ):

                try:

                    plan.fail()

                except Exception:
                    pass

            # ----------------------------------------------
            # Fail Controller Safely
            # ----------------------------------------------

            if self.controller.is_active():

                try:

                    self.controller.fail(
                        str(exc)
                    )

                except Exception:
                    pass

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
                "error": str(exc),
                "progress": (
                    self.planner.get_progress(
                        plan
                    )
                    if isinstance(
                        plan,
                        AgentPlan,
                    )
                    else None
                ),
            }

    # ========================================================
    # Pause
    # ========================================================

    def pause(self) -> bool:
        """
        Pause the current execution.
        """

        try:

            return self.controller.pause()

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to pause execution: {exc}"
            ) from exc

    # ========================================================
    # Resume
    # ========================================================

    def resume(self) -> bool:
        """
        Resume the current execution.
        """

        try:

            return self.controller.resume()

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to resume execution: {exc}"
            ) from exc

    # ========================================================
    # Cancel
    # ========================================================

    def cancel(self) -> bool:
        """
        Cancel the current execution.
        """

        try:

            result = self.controller.cancel()

            return result

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to cancel execution: {exc}"
            ) from exc

    # ========================================================
    # Retry
    # ========================================================

    def retry_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Retry a failed step through the execution controller.
        """

        try:

            return self.controller.retry_step(
                step
            )

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to retry step: {exc}"
            ) from exc

    # ========================================================
    # Skip
    # ========================================================

    def skip_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Skip a pending step through the execution controller.
        """

        try:

            return self.controller.skip_step(
                step
            )

        except AgentExecutionControllerError as exc:

            raise AgentOrchestratorError(
                f"Unable to skip step: {exc}"
            ) from exc

    # ========================================================
    # Execution State
    # ========================================================

    def is_running(self) -> bool:
        """
        Return True when execution is running.
        """

        return self.controller.is_running()

    def is_paused(self) -> bool:
        """
        Return True when execution is paused.
        """

        return self.controller.is_paused()

    def is_cancelled(self) -> bool:
        """
        Return True when execution is cancelled.
        """

        return self.controller.is_cancelled()

    def is_completed(self) -> bool:
        """
        Return True when execution is completed.
        """

        return self.controller.is_completed()

    def is_failed(self) -> bool:
        """
        Return True when execution has failed.
        """

        return self.controller.is_failed()

    def is_active(self) -> bool:
        """
        Return True when execution is active.
        """

        return self.controller.is_active()

    # ========================================================
    # Controller Status
    # ========================================================

    def get_execution_status(self) -> Dict[str, Any]:
        """
        Return execution controller status.
        """

        return self.controller.get_status()

    # ========================================================
    # Execution History
    # ========================================================

    def get_execution_history(self):
        """
        Return execution lifecycle history.
        """

        return self.controller.get_history()

    # ========================================================
    # Progress
    # ========================================================

    def get_progress(
        self,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """
        Return current execution progress.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
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
        """
        Reset the execution controller.
        """

        try:

            return self.controller.reset()

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
            f"controller={self.controller!r}"
            ")"
        )