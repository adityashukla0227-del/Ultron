"""
ULTRON Voice Command Executor

v0.60 — Voice Command Execution

Responsibilities:
- Read a command from AgentRuntimeContext
- Resolve the command to an existing AgentTool
- Create an execution plan
- Delegate execution to AgentOrchestrator
- Synchronize runtime context state
- Return a structured execution result

The VoiceCommandExecutor does NOT:
- Perform STT
- Execute tools directly
- Create a new execution engine
- Replace AgentPlanner
- Replace AgentOrchestrator
"""

from typing import Any, Dict, Optional

from modules.agent.agent_orchestrator import (
    AgentOrchestrator,
    AgentOrchestratorError,
)
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanner,
)
from modules.agent.agent_runtime_context import (
    AgentRuntimeContext,
)


class VoiceCommandExecutorError(Exception):
    """Base exception for VoiceCommandExecutor errors."""


class VoiceCommandExecutor:
    """
    Bridge between voice-derived runtime queries and the existing
    agent execution architecture.
    """

    def __init__(
        self,
        runtime_context: AgentRuntimeContext,
        planner: AgentPlanner,
        orchestrator: AgentOrchestrator,
    ) -> None:
        if not isinstance(runtime_context, AgentRuntimeContext):
            raise ValueError(
                "runtime_context must be an AgentRuntimeContext"
            )

        if not isinstance(planner, AgentPlanner):
            raise ValueError(
                "planner must be an AgentPlanner"
            )

        if not isinstance(orchestrator, AgentOrchestrator):
            raise ValueError(
                "orchestrator must be an AgentOrchestrator"
            )

        self._runtime_context = runtime_context
        self._planner = planner
        self._orchestrator = orchestrator

    # ========================================================
    # Properties
    # ========================================================

    @property
    def runtime_context(self) -> AgentRuntimeContext:
        """Return the runtime context."""
        return self._runtime_context

    @property
    def planner(self) -> AgentPlanner:
        """Return the agent planner."""
        return self._planner

    @property
    def orchestrator(self) -> AgentOrchestrator:
        """Return the agent orchestrator."""
        return self._orchestrator

    # ========================================================
    # Execution Identity
    # ========================================================

    def _execution_id(
        self,
        plan: Optional[AgentPlan] = None,
    ) -> Optional[str]:
        """
        Return the canonical execution identifier.

        AgentOrchestrator derives execution identity from the plan ID.
        The controller ID is used only as a defensive fallback when
        no plan is available.
        """

        if plan is not None:
            return str(plan.id)

        controller_execution_id = getattr(
            self._orchestrator.controller,
            "execution_id",
            None,
        )

        if controller_execution_id is not None:
            return str(controller_execution_id)

        return None

    # ========================================================
    # Execute Voice Command
    # ========================================================

    def execute(self) -> Dict[str, Any]:
        """
        Execute the command stored in the runtime context.

        The command is resolved through the existing AgentEngine /
        ToolSelector architecture. A plan is then created and delegated
        to AgentOrchestrator for execution.

        Returns:
            Structured execution result.
        """

        context = self._runtime_context

        query = context.get_query()

        # ----------------------------------------------------
        # Validate Query Type
        # ----------------------------------------------------

        if not isinstance(query, str):
            return self._failure_result(
                error="Runtime context query must be a string."
            )

        query = query.strip()

        # ----------------------------------------------------
        # Validate Query Content
        # ----------------------------------------------------

        if not query:
            return self._failure_result(
                error="Runtime context query is empty."
            )

        # ----------------------------------------------------
        # Validate Agent
        # ----------------------------------------------------

        agent = context.agent

        if agent is None:
            return self._failure_result(
                query=query,
                error="Runtime context has no agent.",
            )

        try:
            # ------------------------------------------------
            # Planning State
            # ------------------------------------------------

            context.set_status("planning")

            # ------------------------------------------------
            # Resolve Tool
            # ------------------------------------------------

            tool = self._orchestrator.engine.select_tool(
                agent,
                query,
            )

            if tool is None:
                context.set_status("failed")

                return self._failure_result(
                    query=query,
                    error=(
                        f"No suitable tool found for command: "
                        f"{query}"
                    ),
                )

            # ------------------------------------------------
            # Validate Resolved Tool
            # ------------------------------------------------

            tool_name = getattr(
                tool,
                "name",
                None,
            )

            if (
                not isinstance(tool_name, str)
                or not tool_name.strip()
            ):
                context.set_status("failed")

                return self._failure_result(
                    query=query,
                    error="Resolved tool has no valid name.",
                )

            # ------------------------------------------------
            # Create Plan
            # ------------------------------------------------

            plan = self._planner.create_plan(
                agent=agent,
                name="Voice Command",
                description=query,
            )

            # ------------------------------------------------
            # Create Single Execution Step
            # ------------------------------------------------

            step = self._planner.create_step(
                action=tool_name,
                description=query,
                parameters={},
                tool_name=tool_name,
            )

            self._planner.add_step(
                plan,
                step,
            )

            # ------------------------------------------------
            # Prepare Plan
            # ------------------------------------------------

            self._planner.prepare_plan(
                plan
            )

            # ------------------------------------------------
            # Synchronize Runtime Context
            # ------------------------------------------------

            context.set_plan(
                plan
            )

            context.set_status(
                "planned"
            )

            # ------------------------------------------------
            # Delegate Execution
            # ------------------------------------------------

            result = self._orchestrator.execute_plan(
                agent,
                plan,
            )

            # ------------------------------------------------
            # Validate Orchestrator Result
            # ------------------------------------------------

            if not isinstance(result, dict):
                context.set_status("failed")

                return self._failure_result(
                    query=query,
                    plan=plan,
                    tool_name=tool_name,
                    error=(
                        "AgentOrchestrator returned "
                        "an invalid result."
                    ),
                )

            execution_id = self._execution_id(
                plan
            )

            # ------------------------------------------------
            # Successful Execution
            # ------------------------------------------------

            if result.get("success") is True:
                context.set_status(
                    "completed"
                )

                return {
                    "success": True,
                    "query": query,
                    "context_id": context.id,
                    "plan_id": plan.id,
                    "execution_id": execution_id,
                    "tool_name": tool_name,
                    "result": result.get("result"),
                    "status": "completed",
                    "progress": result.get("progress"),
                }

            # ------------------------------------------------
            # Failed Execution
            # ------------------------------------------------

            context.set_status(
                "failed"
            )

            return {
                "success": False,
                "query": query,
                "context_id": context.id,
                "plan_id": plan.id,
                "execution_id": execution_id,
                "tool_name": tool_name,
                "error": result.get(
                    "error",
                    "Voice command execution failed.",
                ),
                "status": "failed",
                "progress": result.get("progress"),
            }

        # ----------------------------------------------------
        # Orchestrator Failure
        # ----------------------------------------------------

        except AgentOrchestratorError as exc:
            context.set_status(
                "failed"
            )

            return self._failure_result(
                query=query,
                error=str(exc),
            )

        # ----------------------------------------------------
        # Defensive Failure
        # ----------------------------------------------------

        except Exception as exc:
            context.set_status(
                "failed"
            )

            return self._failure_result(
                query=query,
                error=str(exc),
            )

    # ========================================================
    # Failure Result
    # ========================================================

    def _failure_result(
        self,
        query: Optional[str] = None,
        plan: Optional[AgentPlan] = None,
        tool_name: Optional[str] = None,
        error: str = "Voice command execution failed.",
    ) -> Dict[str, Any]:
        """
        Build a normalized failure result.
        """

        return {
            "success": False,
            "query": query,
            "context_id": self._runtime_context.id,
            "plan_id": (
                plan.id
                if plan is not None
                else None
            ),
            "execution_id": self._execution_id(
                plan
            ),
            "tool_name": tool_name,
            "error": error,
            "status": "failed",
        }


__all__ = [
    "VoiceCommandExecutor",
    "VoiceCommandExecutorError",
]