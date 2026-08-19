"""
Ultron Agent Engine
Version: v0.37

Execution engine for Ultron AI Agents.

Responsibilities:
- Validate agents before execution
- Execute registered agent actions
- Manage execution context
- Track execution results
- Handle execution errors safely
- Provide a clean foundation for future AI-powered agents

The engine does NOT decide how an agent is persisted.
Persistence belongs to the registry/storage layers.
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from modules.agent.agent import Agent


class AgentEngineError(Exception):
    """Base exception for agent engine errors."""


class AgentExecutionError(AgentEngineError):
    """Raised when an agent cannot be executed."""


class AgentEngine:
    """
    Core execution engine for Ultron agents.

    The engine maintains a runtime action registry.

    An agent specifies an action name. The engine resolves that
    action to a registered Python callable and executes it using
    the agent's parameters.

    This architecture allows future expansion into:

    - AI model execution
    - Tool calling
    - Browser automation
    - Computer control
    - Voice interaction
    - Vision
    - Workflow execution
    - Multi-agent collaboration
    """

    def __init__(self) -> None:
        self._actions: Dict[
            str,
            Callable[..., Any],
        ] = {}

    # ========================================================
    # Action Registration
    # ========================================================

    def register_action(
        self,
        action_name: str,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Register an executable agent action.

        Args:
            action_name:
                Unique name used by an Agent.

            handler:
                Callable that performs the action.

        Returns:
            True when registration succeeds.
        """

        if not isinstance(
            action_name,
            str,
        ) or not action_name.strip():

            raise AgentEngineError(
                "Action name must be a non-empty string."
            )

        if not callable(handler):
            raise AgentEngineError(
                "Action handler must be callable."
            )

        normalized_name = (
            action_name.strip().lower()
        )

        self._actions[
            normalized_name
        ] = handler

        return True

    # ========================================================
    # Action Lookup
    # ========================================================

    def get_action(
        self,
        action_name: str,
    ) -> Optional[
        Callable[..., Any]
    ]:
        """
        Return a registered action handler.
        """

        if not isinstance(
            action_name,
            str,
        ):
            return None

        return self._actions.get(
            action_name.strip().lower()
        )

    # ========================================================
    # Action Existence
    # ========================================================

    def has_action(
        self,
        action_name: str,
    ) -> bool:
        """
        Check whether an action exists.
        """

        return (
            self.get_action(
                action_name
            )
            is not None
        )

    # ========================================================
    # Action Removal
    # ========================================================

    def remove_action(
        self,
        action_name: str,
    ) -> bool:
        """
        Remove an action from the runtime registry.

        Returns:
            True if removed, otherwise False.
        """

        if not isinstance(
            action_name,
            str,
        ):
            return False

        normalized_name = (
            action_name.strip().lower()
        )

        if normalized_name not in self._actions:
            return False

        del self._actions[
            normalized_name
        ]

        return True

    # ========================================================
    # Action Listing
    # ========================================================

    def list_actions(self) -> list[str]:
        """
        Return all registered action names.
        """

        return list(
            self._actions.keys()
        )

    # ========================================================
    # Agent Validation
    # ========================================================

    def validate_agent(
        self,
        agent: Agent,
    ) -> bool:
        """
        Validate an Agent before execution.

        Returns:
            True when the agent is executable.

        Raises:
            AgentExecutionError:
                If the agent is invalid or inactive.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentExecutionError(
                "Only Agent instances can be executed."
            )

        try:
            agent.validate()
        except Exception as exc:
            raise AgentExecutionError(
                f"Agent validation failed: {exc}"
            ) from exc

        if not agent.is_active():
            raise AgentExecutionError(
                f"Agent is not active: {agent.id}"
            )

        if not agent.action:
            raise AgentExecutionError(
                f"Agent has no action: {agent.id}"
            )

        if not self.has_action(
            agent.action
        ):
            raise AgentExecutionError(
                f"Action handler not found: "
                f"{agent.action}"
            )

        return True

    # ========================================================
    # Execute
    # ========================================================

    def execute(
        self,
        agent: Agent,
        **runtime_parameters: Any,
    ) -> Any:
        """
        Execute an Agent.

        Runtime parameters override parameters stored
        inside the agent.

        Example:

            engine.execute(
                agent,
                message="Hello"
            )

        Returns:
            Result returned by the registered action.
        """

        self.validate_agent(
            agent
        )

        handler = self.get_action(
            agent.action
        )

        if handler is None:
            raise AgentExecutionError(
                f"Action handler not found: "
                f"{agent.action}"
            )

        parameters = dict(
            agent.parameters or {}
        )

        parameters.update(
            runtime_parameters
        )

        started_at = datetime.now()

        try:

            result = handler(
                **parameters
            )

            finished_at = datetime.now()

            self._record_success(
                agent=agent,
                result=result,
                started_at=started_at,
                finished_at=finished_at,
            )

            return result

        except Exception as exc:

            finished_at = datetime.now()

            self._record_failure(
                agent=agent,
                error=exc,
                started_at=started_at,
                finished_at=finished_at,
            )

            raise AgentExecutionError(
                f"Agent execution failed: {exc}"
            ) from exc

    # ========================================================
    # Success Tracking
    # ========================================================

    def _record_success(
        self,
        agent: Agent,
        result: Any,
        started_at: datetime,
        finished_at: datetime,
    ) -> None:
        """
        Record successful execution state.
        """

        agent.last_run = (
            finished_at.isoformat()
        )

        agent.last_result = result

        if hasattr(
            agent,
            "last_error",
        ):
            agent.last_error = None

        if hasattr(
            agent,
            "execution_count",
        ):
            agent.execution_count += 1

        if hasattr(
            agent,
            "last_execution_started",
        ):
            agent.last_execution_started = (
                started_at.isoformat()
            )

        if hasattr(
            agent,
            "last_execution_finished",
        ):
            agent.last_execution_finished = (
                finished_at.isoformat()
            )

    # ========================================================
    # Failure Tracking
    # ========================================================

    def _record_failure(
        self,
        agent: Agent,
        error: Exception,
        started_at: datetime,
        finished_at: datetime,
    ) -> None:
        """
        Record failed execution state.
        """

        agent.last_run = (
            finished_at.isoformat()
        )

        agent.last_result = {
            "success": False,
            "error": str(error),
        }

        if hasattr(
            agent,
            "last_error",
        ):
            agent.last_error = str(
                error
            )

        if hasattr(
            agent,
            "execution_count",
        ):
            agent.execution_count += 1

        if hasattr(
            agent,
            "last_execution_started",
        ):
            agent.last_execution_started = (
                started_at.isoformat()
            )

        if hasattr(
            agent,
            "last_execution_finished",
        ):
            agent.last_execution_finished = (
                finished_at.isoformat()
            )

    # ========================================================
    # Execute By ID
    # ========================================================

    def execute_by_id(
        self,
        agent_id: str,
        registry: Any,
        **runtime_parameters: Any,
    ) -> Any:
        """
        Resolve an Agent from a registry and execute it.

        The registry is intentionally accepted as a dependency
        instead of being owned by the engine.
        """

        if registry is None:
            raise AgentExecutionError(
                "Agent registry is required."
            )

        try:
            agent = registry.get(
                agent_id
            )
        except Exception as exc:
            raise AgentExecutionError(
                f"Unable to retrieve agent: {exc}"
            ) from exc

        if agent is None:
            raise AgentExecutionError(
                f"Agent not found: {agent_id}"
            )

        return self.execute(
            agent,
            **runtime_parameters,
        )

    # ========================================================
    # Execute Safely
    # ========================================================

    def execute_safe(
        self,
        agent: Agent,
        **runtime_parameters: Any,
    ) -> Dict[str, Any]:
        """
        Execute an agent without propagating execution errors.

        Returns a standardized result dictionary.

        This will be useful later for API responses,
        background workers and agent orchestration.
        """

        started_at = datetime.now()

        try:

            result = self.execute(
                agent,
                **runtime_parameters,
            )

            return {
                "success": True,
                "agent_id": agent.id,
                "result": result,
                "started_at": started_at.isoformat(),
                "finished_at": datetime.now().isoformat(),
                "error": None,
            }

        except Exception as exc:

            return {
                "success": False,
                "agent_id": getattr(
                    agent,
                    "id",
                    None,
                ),
                "result": None,
                "started_at": started_at.isoformat(),
                "finished_at": datetime.now().isoformat(),
                "error": str(exc),
            }

    # ========================================================
    # Reset
    # ========================================================

    def clear_actions(self) -> None:
        """
        Remove all registered runtime actions.
        """

        self._actions.clear()

    # ========================================================
    # Representation
    # ========================================================

    def __len__(self) -> int:
        """
        Return number of registered actions.
        """

        return len(
            self._actions
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"AgentEngine("
            f"actions={len(self._actions)}"
            f")"
        )