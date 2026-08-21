"""
Ultron Agent Engine
Version: v0.38

Execution engine for Ultron AI Agents.

Responsibilities:
- Validate agents before execution
- Execute registered agent actions
- Resolve and execute agent tools
- Enforce agent tool permissions
- Select tools for agents
- Manage execution context
- Track execution results
- Handle execution errors safely
- Provide standardized safe tool execution
- Provide a foundation for future AI-powered agents

The engine does NOT decide how an agent is persisted.
Persistence belongs to the registry/storage layers.
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from modules.agent.agent import Agent
from modules.agent.tool_registry import ToolRegistry
from modules.agent.tool_result import ToolResult
from modules.agent.tool_selector import ToolSelector


class AgentEngineError(Exception):
    """Base exception for agent engine errors."""


class AgentExecutionError(AgentEngineError):
    """Raised when an agent cannot be executed."""


class AgentEngine:
    """
    Core execution engine for Ultron agents.

    The engine maintains:
    - Runtime action registry
    - ToolRegistry
    - ToolSelector

    An agent specifies an action name.
    The engine resolves that action to a Python callable.

    Agent tools are resolved through ToolRegistry.

    Tool selection is delegated to ToolSelector.
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:

        self._actions: Dict[
            str,
            Callable[..., Any],
        ] = {}

        self.tool_registry = (
            tool_registry
            if tool_registry is not None
            else ToolRegistry()
        )

        self.tool_selector = ToolSelector()

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
    # Tool Registry
    # ========================================================

    def register_tool(
        self,
        tool,
    ) -> bool:
        """
        Register an AgentTool in the engine's ToolRegistry.
        """

        try:

            return self.tool_registry.register(
                tool
            )

        except Exception as exc:

            raise AgentEngineError(
                f"Tool registration failed: {exc}"
            ) from exc

    def remove_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Remove a tool from the engine's ToolRegistry.
        """

        try:

            return self.tool_registry.unregister(
                tool_name
            )

        except Exception as exc:

            raise AgentEngineError(
                f"Tool removal failed: {exc}"
            ) from exc

    def get_tool(
        self,
        tool_name: str,
    ):
        """
        Retrieve a tool from the ToolRegistry.
        """

        return self.tool_registry.get(
            tool_name
        )

    def has_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Check whether a tool is registered.
        """

        return self.tool_registry.has(
            tool_name
        )

    def list_tools(self) -> list[str]:
        """
        Return all registered tool names.
        """

        return self.tool_registry.list_tool_names()

    # ========================================================
    # Tool Selection
    # ========================================================

    def select_tool(
        self,
        agent: Agent,
        query: str,
    ):
        """
        Select an available tool for an agent.

        Delegates deterministic tool selection
        to ToolSelector.

        Returns:
            Selected AgentTool or None.
        """

        return self.tool_selector.select(
            agent,
            query,
        )

    def get_available_tools(
        self,
        agent: Agent,
    ):
        """
        Return enabled tools assigned to an agent.

        Delegates tool filtering to ToolSelector.
        """

        return self.tool_selector.get_available_tools(
            agent
        )

    def get_available_tool_names(
        self,
        agent: Agent,
    ) -> list[str]:
        """
        Return names of enabled tools assigned to an agent.

        Delegates tool filtering to ToolSelector.
        """

        return self.tool_selector.get_available_tool_names(
            agent
        )

    # ========================================================
    # Agent Tool Validation
    # ========================================================

    def validate_agent_tools(
        self,
        agent: Agent,
    ) -> bool:
        """
        Validate that all tools assigned to an agent
        exist in the ToolRegistry.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentExecutionError(
                "Only Agent instances can be validated."
            )

        for tool in agent.get_tools():

            if not self.has_tool(
                tool.name
            ):

                raise AgentExecutionError(
                    f"Tool not found in registry: "
                    f"{tool.name}"
                )

        return True

    # ========================================================
    # Tool Permission Validation
    # ========================================================

    def _validate_tool_access(
        self,
        agent: Agent,
        tool_name: str,
    ):
        """
        Validate that an agent is allowed to execute
        a specific tool.

        Returns:
            Registered AgentTool.

        Raises:
            AgentExecutionError:
                When permission or registration fails.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentExecutionError(
                "Only Agent instances can execute tools."
            )

        if not isinstance(
            tool_name,
            str,
        ) or not tool_name.strip():

            raise AgentExecutionError(
                "Tool name must be a non-empty string."
            )

        tool_name = tool_name.strip()

        assigned_tool = agent.get_tool(
            tool_name
        )

        if assigned_tool is None:

            raise AgentExecutionError(
                f"Tool '{tool_name}' is not assigned "
                f"to agent '{agent.name}'."
            )

        if not assigned_tool.is_enabled():

            raise AgentExecutionError(
                f"Tool '{tool_name}' is disabled "
                f"for agent '{agent.name}'."
            )

        registered_tool = self.get_tool(
            tool_name
        )

        if registered_tool is None:

            raise AgentExecutionError(
                f"Tool '{tool_name}' is not registered."
            )

        if not registered_tool.is_enabled():

            raise AgentExecutionError(
                f"Tool '{tool_name}' is disabled "
                f"in the registry."
            )

        return registered_tool

    # ========================================================
    # Tool Execution
    # ========================================================

    def execute_tool(
        self,
        agent: Agent,
        tool_name: str,
        **parameters: Any,
    ) -> ToolResult:
        """
        Execute a tool assigned to an agent.

        The tool must:
        1. Exist on the Agent
        2. Exist in the ToolRegistry
        3. Be enabled on the Agent
        4. Be enabled in the Registry

        Returns:
            ToolResult from the executed tool.

        Raises:
            AgentExecutionError:
                If the tool cannot be accessed or executed.
        """

        self._validate_tool_access(
            agent,
            tool_name,
        )

        try:

            result = self.tool_registry.execute(
                tool_name,
                **parameters,
            )

            if not isinstance(
                result,
                ToolResult,
            ):

                raise AgentExecutionError(
                    f"Tool '{tool_name}' returned "
                    f"an invalid result type."
                )

            return result

        except AgentExecutionError:
            raise

        except Exception as exc:

            raise AgentExecutionError(
                f"Tool execution failed: "
                f"{tool_name}: {exc}"
            ) from exc

    # ========================================================
    # Safe Tool Execution
    # ========================================================

    def execute_tool_safe(
        self,
        agent: Agent,
        tool_name: str,
        **parameters: Any,
    ) -> ToolResult:
        """
        Safely execute a tool assigned to an agent.

        Every execution path returns a ToolResult.

        This method does not propagate AgentExecutionError
        to the caller.

        Useful for:
        - AI agents
        - API responses
        - Background workers
        - Workflow execution
        - Agent orchestration
        """

        normalized_name = (
            tool_name.strip()
            if isinstance(
                tool_name,
                str,
            )
            else str(tool_name)
        )

        try:

            self._validate_tool_access(
                agent,
                normalized_name,
            )

        except Exception as exc:

            return ToolResult(
                tool_name=normalized_name,
                success=False,
                result=None,
                error=str(exc),
            )

        try:

            result = self.tool_registry.execute_safe(
                normalized_name,
                **parameters,
            )

            if isinstance(
                result,
                ToolResult,
            ):
                return result

            return ToolResult(
                tool_name=normalized_name,
                success=True,
                result=result,
                error=None,
            )

        except Exception as exc:

            return ToolResult(
                tool_name=normalized_name,
                success=False,
                result=None,
                error=str(exc),
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
    # Execute Safe
    # ========================================================

    def execute_safe(
        self,
        agent: Agent,
        **runtime_parameters: Any,
    ) -> Dict[str, Any]:
        """
        Execute an agent without propagating errors.
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

    def clear_tools(self) -> None:
        """
        Remove all registered tools.
        """

        self.tool_registry.clear()

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
            f"actions={len(self._actions)}, "
            f"tools={self.tool_registry.count()}"
            f")"
        )