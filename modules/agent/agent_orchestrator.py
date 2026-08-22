"""
Ultron Agent Orchestrator
Version: v0.41

Execution orchestration layer for Ultron AI Agents.

Responsibilities:
- Validate execution plans
- Start plan execution
- Execute plan steps sequentially
- Resolve step tools through AgentEngine
- Record step results
- Handle step failures safely
- Track plan progress
- Complete or fail plans
- Provide safe plan execution

The AgentOrchestrator does NOT create plans.
Planning belongs to AgentPlanner.

The AgentOrchestrator does NOT directly execute tools.
Tool execution belongs to AgentEngine.
"""

from typing import Any, Dict, Optional

from modules.agent.agent import Agent
from modules.agent.agent_engine import (
    AgentEngine,
    AgentExecutionError,
)
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanError,
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
            v
        AgentEngine
            |
            v
        ToolSelector / ToolRegistry / Tool
    """

    def __init__(
        self,
        engine: Optional[AgentEngine] = None,
        planner: Optional[AgentPlanner] = None,
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

        Action-only execution can be added later without
        changing the orchestration contract.
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

        step.start()

        result = self.engine.execute_tool_safe(
            agent,
            step.tool_name,
            **step.parameters,
        )

        if not isinstance(
            result,
            ToolResult,
        ):
            step.fail(
                "AgentEngine returned an invalid tool result."
            )

            raise AgentOrchestratorError(
                f"Invalid tool result for step: {step.id}"
            )

        if result.success:
            step.complete(
                result.result
            )

            return result

        step.fail(
            result.error
            or "Tool execution failed."
        )

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
        """

        self.validate_plan(
            plan,
            agent,
        )

        if plan.is_draft():
            try:
                plan.prepare()
            except Exception as exc:
                raise AgentOrchestratorError(
                    f"Unable to prepare plan: {exc}"
                ) from exc

        if not plan.is_ready():
            raise AgentOrchestratorError(
                f"Plan is not ready for execution: "
                f"{plan.status}"
            )

        plan.start()

        while True:

            step = self.get_next_step(
                plan
            )

            if step is None:
                break

            result = self.execute_step(
                agent,
                step,
            )

            if (
                isinstance(result, ToolResult)
                and not result.success
            ):
                plan.fail()

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

        if not plan.is_complete():
            plan.fail()

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

        plan.complete()

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

            if (
                isinstance(plan, AgentPlan)
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
                    self.planner.get_progress(plan)
                    if isinstance(
                        plan,
                        AgentPlan,
                    )
                    else None
                ),
            }

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
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "AgentOrchestrator("
            f"engine={self.engine!r}, "
            f"planner={self.planner!r}"
            ")"
        )