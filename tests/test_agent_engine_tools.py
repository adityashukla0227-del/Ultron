"""
Ultron Agent Engine Tool Integration Tests
Version: v0.39

Tests:
- Tool registration through AgentEngine
- Tool retrieval
- Tool availability
- Agent tool assignment
- Agent tool execution
- Runtime parameter passing
- Runtime parameter override
- Tool permission enforcement
- Agent-level disabled tool
- Registry-level disabled tool
- Missing tool handling
- Safe tool execution
- Tool execution failure handling
- Tool validation
"""


import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import (
    AgentEngine,
    AgentExecutionError,
)
from modules.agent.tool import AgentTool
from modules.agent.tool_result import ToolResult


# ============================================================
# Helper
# ============================================================


def create_echo_tool():
    return AgentTool(
        name="echo",
        description="Echo text",
        handler=lambda message: message,
    )


# ============================================================
# Engine Tool Registration
# ============================================================


def test_engine_register_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    result = engine.register_tool(tool)

    assert result is True
    assert engine.has_tool("echo") is True


def test_engine_get_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    result = engine.get_tool("echo")

    assert result is tool


def test_engine_list_tools():

    engine = AgentEngine()

    first = AgentTool(
        name="echo",
        handler=lambda message: message,
    )

    second = AgentTool(
        name="calculator",
        handler=lambda a, b: a + b,
    )

    engine.register_tool(first)
    engine.register_tool(second)

    tools = engine.list_tools()

    assert "echo" in tools
    assert "calculator" in tools
    assert len(tools) == 2


def test_engine_has_missing_tool():

    engine = AgentEngine()

    assert engine.has_tool("missing") is False


def test_engine_remove_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    assert engine.remove_tool("echo") is True
    assert engine.has_tool("echo") is False


# ============================================================
# Agent Tool Assignment
# ============================================================


def test_agent_can_assign_tool():

    agent = Agent(
        name="Tool Agent",
        action="run",
    )

    result = agent.add_tool(
        create_echo_tool()
    )

    assert result is True
    assert agent.get_tool("echo") is not None


def test_agent_tool_assignment_required_for_execution():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Restricted Agent",
        action="run",
    )

    with pytest.raises(
        AgentExecutionError
    ):

        engine.execute_tool(
            agent,
            "echo",
            message="Hello",
        )


# ============================================================
# Agent Tool Execution
# ============================================================


def test_engine_execute_agent_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Echo Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool(
        agent,
        "echo",
        message="Hello Ultron",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.result == "Hello Ultron"
    assert result.tool_name == "echo"


def test_engine_execute_tool_with_parameters():

    engine = AgentEngine()

    tool = AgentTool(
        name="calculator",
        handler=lambda a, b: a + b,
    )

    engine.register_tool(tool)

    agent = Agent(
        name="Calculator Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool(
        agent,
        "calculator",
        a=10,
        b=20,
    )

    assert result.success is True
    assert result.result == 30


def test_engine_tool_runtime_parameters():

    engine = AgentEngine()

    tool = AgentTool(
        name="echo",
        config={
            "message": "Stored",
        },
        handler=lambda message: message,
    )

    engine.register_tool(tool)

    agent = Agent(
        name="Override Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool(
        agent,
        "echo",
        message="Runtime",
    )

    assert result.success is True
    assert result.result == "Runtime"


# ============================================================
# Tool Permission Validation
# ============================================================


def test_engine_rejects_unassigned_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Limited Agent",
        action="run",
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc:

        engine.execute_tool(
            agent,
            "echo",
            message="Hello",
        )

    assert "not assigned" in str(
        exc.value
    )


def test_engine_rejects_disabled_agent_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Disabled Tool Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    agent.disable_tool(
        "echo"
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc:

        engine.execute_tool(
            agent,
            "echo",
            message="Hello",
        )

    assert "disabled" in str(
        exc.value
    )


def test_engine_rejects_disabled_registry_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Registry Disabled Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    tool.disable()

    with pytest.raises(
        AgentExecutionError
    ) as exc:

        engine.execute_tool(
            agent,
            "echo",
            message="Hello",
        )

    assert "disabled" in str(
        exc.value
    )


def test_engine_rejects_missing_registered_tool():

    engine = AgentEngine()

    tool = create_echo_tool()

    agent = Agent(
        name="Missing Registry Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc:

        engine.execute_tool(
            agent,
            "echo",
            message="Hello",
        )

    assert "not registered" in str(
        exc.value
    )


# ============================================================
# Agent Tool Validation
# ============================================================


def test_validate_agent_tools_success():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Valid Tool Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    assert engine.validate_agent_tools(
        agent
    ) is True


def test_validate_agent_tools_missing():

    engine = AgentEngine()

    tool = create_echo_tool()

    agent = Agent(
        name="Invalid Tool Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    with pytest.raises(
        AgentExecutionError
    ) as exc:

        engine.validate_agent_tools(
            agent
        )

    assert "not found in registry" in str(
        exc.value
    )


# ============================================================
# Safe Tool Execution
# ============================================================


def test_engine_execute_tool_safe_success():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Safe Tool Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool_safe(
        agent,
        "echo",
        message="Safe Hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.result == "Safe Hello"
    assert result.error is None


def test_engine_execute_tool_safe_unassigned():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Safe Restricted Agent",
        action="run",
    )

    result = engine.execute_tool_safe(
        agent,
        "echo",
        message="Hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert "not assigned" in result.error


def test_engine_execute_tool_safe_missing():

    engine = AgentEngine()

    agent = Agent(
        name="Safe Missing Agent",
        action="run",
        tools=[
            AgentTool(
                name="missing",
            ),
        ],
    )

    result = engine.execute_tool_safe(
        agent,
        "missing",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert "not registered" in result.error


def test_engine_execute_tool_safe_disabled():

    engine = AgentEngine()

    tool = create_echo_tool()

    engine.register_tool(tool)

    agent = Agent(
        name="Safe Disabled Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    tool.disable()

    result = engine.execute_tool_safe(
        agent,
        "echo",
        message="Hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert "disabled" in result.error


# ============================================================
# Tool Execution Failure
# ============================================================


def test_engine_tool_execution_failure():

    def failing_tool():

        raise RuntimeError(
            "Tool execution failed"
        )

    engine = AgentEngine()

    tool = AgentTool(
        name="failing",
        handler=failing_tool,
    )

    engine.register_tool(tool)

    agent = Agent(
        name="Failing Tool Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool(
        agent,
        "failing",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert "Tool execution failed" in result.error


def test_engine_tool_safe_execution_failure():

    def failing_tool():

        raise RuntimeError(
            "Safe failure"
        )

    engine = AgentEngine()

    tool = AgentTool(
        name="failing",
        handler=failing_tool,
    )

    engine.register_tool(tool)

    agent = Agent(
        name="Safe Failing Agent",
        action="run",
        tools=[
            tool,
        ],
    )

    result = engine.execute_tool_safe(
        agent,
        "failing",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert "Safe failure" in result.error


# ============================================================
# Multiple Tools
# ============================================================


def test_agent_can_use_multiple_tools():

    engine = AgentEngine()

    echo = AgentTool(
        name="echo",
        handler=lambda message: message,
    )

    calculator = AgentTool(
        name="calculator",
        handler=lambda a, b: a + b,
    )

    engine.register_tool(echo)
    engine.register_tool(calculator)

    agent = Agent(
        name="Multi Tool Agent",
        action="run",
        tools=[
            echo,
            calculator,
        ],
    )

    echo_result = engine.execute_tool(
        agent,
        "echo",
        message="Ultron",
    )

    calculator_result = engine.execute_tool(
        agent,
        "calculator",
        a=5,
        b=7,
    )

    assert echo_result.success is True
    assert echo_result.result == "Ultron"

    assert calculator_result.success is True
    assert calculator_result.result == 12


# ============================================================
# Engine Tool Cleanup
# ============================================================


def test_engine_clear_tools():

    engine = AgentEngine()

    engine.register_tool(
        create_echo_tool()
    )

    assert engine.has_tool(
        "echo"
    ) is True

    engine.clear_tools()

    assert engine.has_tool(
        "echo"
    ) is False

    assert engine.list_tools() == []