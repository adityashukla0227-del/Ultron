"""
Ultron Agent Engine Capability Tests

v0.97 — Platform Integration

Tests:
- CapabilityRegistry injection
- CapabilityRegistry default behavior
- Capability → AgentTool discovery
- Capability resolution
- Ambiguous capability resolution
- Capability-based tool execution
- Capability execution through the standard
  AgentEngine authorization boundary
- Capability execution must not bypass authorization
- Safe capability execution
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import (
    AgentEngine,
    AgentExecutionError,
)
from modules.agent.authorization import AuthorizationService
from modules.agent.capability import Capability
from modules.agent.capability_registry import CapabilityRegistry
from modules.agent.permission import Permission
from modules.agent.permission_registry import PermissionRegistry
from modules.agent.tool import AgentTool
from modules.agent.tool_permission_mapping import ToolPermissionMapping


def _handler(**kwargs):
    """Simple test handler."""
    return kwargs


def _create_tool(
    name="test_tool",
    capabilities=None,
):
    """Create a test AgentTool."""
    return AgentTool(
        name=name,
        description=f"{name} test tool",
        handler=_handler,
        capabilities=capabilities or [],
    )


def _create_agent(
    name="Test Agent",
    tools=None,
):
    """Create a test Agent."""
    return Agent(
        name=name,
        description="Capability integration test agent",
        action="test_action",
        tools=tools or [],
    )


class TestAgentEngineCapabilityResolution:
    """Tests for AgentEngine capability integration."""

    def test_capability_registry_is_injected(self):
        """
        AgentEngine must preserve an explicitly supplied
        CapabilityRegistry instance.
        """

        registry = CapabilityRegistry()

        engine = AgentEngine(
            capability_registry=registry,
        )

        assert engine.capability_registry is registry

    def test_capability_registry_defaults_when_not_provided(self):
        """
        AgentEngine must create a CapabilityRegistry when
        none is explicitly supplied.
        """

        engine = AgentEngine()

        assert isinstance(
            engine.capability_registry,
            CapabilityRegistry,
        )

    def test_capability_resolves_single_matching_tool(self):
        """
        CapabilityRegistry must discover exactly one tool
        supporting a requested capability.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        matches = engine.capability_registry.get_tools_for_capability(
            "calculation",
            agent.get_tools(),
        )

        assert matches == [tool]

    def test_capability_returns_no_tools_when_not_supported(self):
        """
        A capability with no matching AgentTool must return
        an empty discovery result.
        """

        capability = Capability(
            name="web_search",
            description="Web search capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[tool],
        )

        matches = engine.capability_registry.get_tools_for_capability(
            "web_search",
            agent.get_tools(),
        )

        assert matches == []

    def test_capability_returns_multiple_matching_tools(self):
        """
        Capability discovery must return all matching tools
        when multiple tools advertise the same capability.
        """

        capability = Capability(
            name="search",
            description="Search capability",
        )

        web_tool = _create_tool(
            name="web_search",
            capabilities=["search"],
        )

        database_tool = _create_tool(
            name="database_search",
            capabilities=["search"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[
                web_tool,
                database_tool,
            ],
        )

        matches = engine.capability_registry.get_tools_for_capability(
            "search",
            agent.get_tools(),
        )

        assert matches == [
            web_tool,
            database_tool,
        ]

    def test_capability_resolution_normalizes_capability_name(self):
        """
        Capability discovery must normalize surrounding whitespace.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        matches = engine.capability_registry.get_tools_for_capability(
            "  calculation  ",
            agent.get_tools(),
        )

        assert matches == [tool]

    def test_capability_resolution_does_not_modify_agent_tools(self):
        """
        Capability discovery must not mutate the agent's tool list.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        original_tools = agent.get_tools()

        engine.capability_registry.get_tools_for_capability(
            "calculation",
            agent.get_tools(),
        )

        assert agent.get_tools() == original_tools

    def test_resolve_capability_returns_single_matching_tool(self):
        """
        resolve_capability() must return the single matching tool.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        resolved = engine.resolve_capability(
            agent,
            "calculation",
        )

        assert resolved is tool

    def test_resolve_capability_returns_none_when_no_tool_matches(self):
        """
        resolve_capability() must return None when no tool
        supports the requested capability.
        """

        capability = Capability(
            name="web_search",
            description="Web search capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[tool],
        )

        resolved = engine.resolve_capability(
            agent,
            "web_search",
        )

        assert resolved is None

    def test_resolve_capability_rejects_ambiguous_tools(self):
        """
        resolve_capability() must not arbitrarily select a tool
        when multiple tools provide the same capability.
        """

        capability = Capability(
            name="search",
            description="Search capability",
        )

        web_tool = _create_tool(
            name="web_search",
            capabilities=["search"],
        )

        database_tool = _create_tool(
            name="database_search",
            capabilities=["search"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[
                web_tool,
                database_tool,
            ],
        )

        resolved = engine.resolve_capability(
            agent,
            "search",
        )

        assert resolved is None

    def test_execute_capability_executes_single_matching_tool(self):
        """
        A capability resolving to exactly one tool must
        execute that tool through the AgentEngine execution path.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        permission = Permission(
            name="calculation.execute",
            description="Execute calculation tools",
        )

        permission_registry = PermissionRegistry(
            [permission],
        )

        authorization_service = AuthorizationService(
            permission_registry,
        )

        permission_mapping = ToolPermissionMapping(
            {
                "calculator": [
                    "calculation.execute",
                ],
            }
        )

        engine = AgentEngine(
            capability_registry=registry,
            authorization_service=authorization_service,
            tool_permission_mapping=permission_mapping,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        engine.tool_registry.register(tool)

        result = engine.execute_capability(
            agent,
            "calculation",
            expression="2 + 3",
        )

        assert result.success is True
        assert result.result == {
            "expression": "2 + 3",
        }

    def test_execute_capability_fails_when_no_tool_matches(self):
        """
        Capability execution must fail when the capability
        cannot be resolved to exactly one tool.
        """

        capability = Capability(
            name="web_search",
            description="Web search capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[tool],
        )

        with pytest.raises(
            AgentExecutionError,
            match=(
                "Capability 'web_search' "
                "could not be resolved to exactly one tool."
            ),
        ):
            engine.execute_capability(
                agent,
                "web_search",
            )

    def test_execute_capability_fails_on_ambiguous_capability(self):
        """
        Capability execution must fail when multiple tools
        provide the same capability.
        """

        capability = Capability(
            name="search",
            description="Search capability",
        )

        web_tool = _create_tool(
            name="web_search",
            capabilities=["search"],
        )

        database_tool = _create_tool(
            name="database_search",
            capabilities=["search"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[
                web_tool,
                database_tool,
            ],
        )

        with pytest.raises(
            AgentExecutionError,
            match=(
                "Capability 'search' "
                "could not be resolved to exactly one tool."
            ),
        ):
            engine.execute_capability(
                agent,
                "search",
            )

    def test_execute_capability_does_not_bypass_authorization(self):
        """
        Capability execution must respect the existing
        AgentEngine authorization boundary.

        A capability may resolve successfully, but the tool
        must not execute when authorization is denied.
        """

        execution_state = {
            "executed": False,
        }

        def protected_handler(**kwargs):
            execution_state["executed"] = True
            return kwargs

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = AgentTool(
            name="calculator",
            description="Protected calculator tool",
            handler=protected_handler,
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        engine.tool_registry.register(tool)

        with pytest.raises(
            AgentExecutionError,
            match="Tool authorization denied",
        ):
            engine.execute_capability(
                agent,
                "calculation",
                expression="2 + 3",
            )

        assert execution_state["executed"] is False

    def test_execute_capability_safe_executes_single_matching_tool(self):
        """
        execute_capability_safe() must execute a uniquely
        resolved capability and return a successful ToolResult.
        """

        capability = Capability(
            name="calculation",
            description="Calculation capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        permission = Permission(
            name="calculation.execute",
            description="Execute calculation tools",
        )

        permission_registry = PermissionRegistry(
            [permission],
        )

        authorization_service = AuthorizationService(
            permission_registry,
        )

        permission_mapping = ToolPermissionMapping(
            {
                "calculator": [
                    "calculation.execute",
                ],
            }
        )

        engine = AgentEngine(
            capability_registry=registry,
            authorization_service=authorization_service,
            tool_permission_mapping=permission_mapping,
        )

        agent = _create_agent(
            name="Calculator Agent",
            tools=[tool],
        )

        engine.tool_registry.register(tool)

        result = engine.execute_capability_safe(
            agent,
            "calculation",
            expression="2 + 3",
        )

        assert result.success is True
        assert result.result == {
            "expression": "2 + 3",
        }

    def test_execute_capability_safe_returns_failure_when_no_tool_matches(
        self,
    ):
        """
        execute_capability_safe() must return a failed ToolResult
        when no tool supports the requested capability.
        """

        capability = Capability(
            name="web_search",
            description="Web search capability",
        )

        tool = _create_tool(
            name="calculator",
            capabilities=["calculation"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[tool],
        )

        result = engine.execute_capability_safe(
            agent,
            "web_search",
        )

        assert result.success is False
        assert (
            "Capability 'web_search' "
            "could not be resolved to exactly one tool."
            in result.error
        )

    def test_execute_capability_safe_returns_failure_on_ambiguous_capability(
        self,
    ):
        """
        execute_capability_safe() must return a failed ToolResult
        when multiple tools provide the same capability.
        """

        capability = Capability(
            name="search",
            description="Search capability",
        )

        web_tool = _create_tool(
            name="web_search",
            capabilities=["search"],
        )

        database_tool = _create_tool(
            name="database_search",
            capabilities=["search"],
        )

        registry = CapabilityRegistry(
            [capability],
        )

        engine = AgentEngine(
            capability_registry=registry,
        )

        agent = _create_agent(
            name="Search Agent",
            tools=[
                web_tool,
                database_tool,
            ],
        )

        result = engine.execute_capability_safe(
            agent,
            "search",
        )

        assert result.success is False
        assert (
            "Capability 'search' "
            "could not be resolved to exactly one tool."
            in result.error
        )