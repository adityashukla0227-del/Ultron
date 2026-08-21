"""
Ultron Agent Tool Selector Integration Tests
Version: v0.39

Tests:
- AgentEngine exposes ToolSelector
- Tool selection through engine
- Exact tool selection
- Description-based selection
- Missing tool selection
- Ambiguous selection
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.tool import AgentTool
from modules.agent.tool_selector import ToolSelector


def create_agent_with_tools():

    agent = Agent(
        name="Selector Agent",
        action="hello",
    )

    weather_tool = AgentTool(
        name="weather",
        description="Get current weather information",
        handler=lambda city: f"Weather for {city}",
    )

    calculator_tool = AgentTool(
        name="calculator",
        description="Perform mathematical calculations",
        handler=lambda expression: expression,
    )

    agent.add_tool(weather_tool)
    agent.add_tool(calculator_tool)

    return agent


def test_engine_has_tool_selector():

    engine = AgentEngine()

    assert isinstance(
        engine.tool_selector,
        ToolSelector,
    )


def test_engine_select_tool_by_name():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "weather",
    )

    assert selected is not None
    assert selected.name == "weather"


def test_engine_select_tool_by_name_with_whitespace():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "  weather  ",
    )

    assert selected is not None
    assert selected.name == "weather"


def test_engine_select_tool_by_description():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "weather information",
    )

    assert selected is not None
    assert selected.name == "weather"


def test_engine_select_calculator_tool():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "mathematical calculations",
    )

    assert selected is not None
    assert selected.name == "calculator"


def test_engine_select_missing_tool():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "unknown tool",
    )

    assert selected is None


def test_engine_select_empty_query():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    selected = engine.select_tool(
        agent,
        "",
    )

    assert selected is None


def test_engine_select_invalid_agent():

    engine = AgentEngine()

    with pytest.raises(Exception):

        engine.select_tool(
            "not-an-agent",
            "weather",
        )


def test_engine_get_available_tools():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    tools = engine.get_available_tools(
        agent
    )

    assert len(tools) == 2

    names = [
        tool.name
        for tool in tools
    ]

    assert "weather" in names
    assert "calculator" in names


def test_engine_get_available_tool_names():

    engine = AgentEngine()

    agent = create_agent_with_tools()

    names = engine.get_available_tool_names(
        agent
    )

    assert "weather" in names
    assert "calculator" in names
    assert len(names) == 2


def test_engine_selector_repr():

    engine = AgentEngine()

    assert repr(
        engine.tool_selector
    ) == "ToolSelector()"