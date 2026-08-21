"""
Ultron Tool Selector Tests
Version: v0.39

Tests:
- ToolSelector creation
- Available tool filtering
- Available tool names
- Exact tool selection
- Description-based candidate search
- Automatic tool selection
- Disabled tool handling
- Invalid input handling
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.tool import AgentTool
from modules.agent.tool_selector import (
    ToolSelector,
    ToolSelectionError,
)


# ============================================================
# Fixtures
# ============================================================


def create_agent():
    """
    Create an agent with multiple tools for testing.
    """

    calculator = AgentTool(
        name="calculator",
        description="Perform mathematical calculations",
    )

    weather = AgentTool(
        name="weather",
        description="Get current weather information",
    )

    search = AgentTool(
        name="search",
        description="Search the internet for information",
    )

    return Agent(
        name="Test Agent",
        action="test",
        tools=[
            calculator,
            weather,
            search,
        ],
    )


# ============================================================
# Creation Tests
# ============================================================


def test_tool_selector_creation():

    selector = ToolSelector()

    assert selector is not None


def test_tool_selector_repr():

    selector = ToolSelector()

    representation = repr(
        selector
    )

    assert "ToolSelector" in representation


# ============================================================
# Available Tool Tests
# ============================================================


def test_get_available_tools():

    selector = ToolSelector()
    agent = create_agent()

    tools = selector.get_available_tools(
        agent
    )

    assert len(tools) == 3
    assert all(
        isinstance(
            tool,
            AgentTool,
        )
        for tool in tools
    )


def test_get_available_tool_names():

    selector = ToolSelector()
    agent = create_agent()

    names = selector.get_available_tool_names(
        agent
    )

    assert names == [
        "calculator",
        "weather",
        "search",
    ]


def test_disabled_tools_are_excluded():

    selector = ToolSelector()
    agent = create_agent()

    agent.disable_tool(
        "weather"
    )

    tools = selector.get_available_tools(
        agent
    )

    names = [
        tool.name
        for tool in tools
    ]

    assert "weather" not in names
    assert "calculator" in names
    assert "search" in names


# ============================================================
# Exact Selection Tests
# ============================================================


def test_select_by_name():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select_by_name(
        agent,
        "calculator",
    )

    assert tool is not None
    assert tool.name == "calculator"


def test_select_by_name_missing():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select_by_name(
        agent,
        "missing",
    )

    assert tool is None


def test_select_by_name_ignores_whitespace():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select_by_name(
        agent,
        " calculator ",
    )

    assert tool is not None
    assert tool.name == "calculator"


def test_select_by_name_disabled_tool():

    selector = ToolSelector()
    agent = create_agent()

    agent.disable_tool(
        "calculator"
    )

    tool = selector.select_by_name(
        agent,
        "calculator",
    )

    assert tool is None


# ============================================================
# Candidate Search Tests
# ============================================================


def test_find_candidates_by_name():

    selector = ToolSelector()
    agent = create_agent()

    candidates = selector.find_candidates(
        agent,
        "weather",
    )

    assert len(candidates) == 1
    assert candidates[0].name == "weather"


def test_find_candidates_by_description():

    selector = ToolSelector()
    agent = create_agent()

    candidates = selector.find_candidates(
        agent,
        "mathematical",
    )

    assert len(candidates) == 1
    assert candidates[0].name == "calculator"


def test_find_candidates_case_insensitive():

    selector = ToolSelector()
    agent = create_agent()

    candidates = selector.find_candidates(
        agent,
        "WEATHER",
    )

    assert len(candidates) == 1
    assert candidates[0].name == "weather"


def test_find_candidates_no_match():

    selector = ToolSelector()
    agent = create_agent()

    candidates = selector.find_candidates(
        agent,
        "music",
    )

    assert candidates == []


def test_find_candidates_empty_query():

    selector = ToolSelector()
    agent = create_agent()

    candidates = selector.find_candidates(
        agent,
        "",
    )

    assert candidates == []


# ============================================================
# Automatic Selection Tests
# ============================================================


def test_select_exact_name():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select(
        agent,
        "calculator",
    )

    assert tool is not None
    assert tool.name == "calculator"


def test_select_single_candidate():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select(
        agent,
        "mathematical",
    )

    assert tool is not None
    assert tool.name == "calculator"


def test_select_no_match():

    selector = ToolSelector()
    agent = create_agent()

    tool = selector.select(
        agent,
        "play music",
    )

    assert tool is None


def test_select_ambiguous_match():

    selector = ToolSelector()

    first = AgentTool(
        name="web_search",
        description="Search the web",
    )

    second = AgentTool(
        name="web_browser",
        description="Browse the web",
    )

    agent = Agent(
        name="Web Agent",
        action="test",
        tools=[
            first,
            second,
        ],
    )

    tool = selector.select(
        agent,
        "web",
    )

    assert tool is None


# ============================================================
# Validation Tests
# ============================================================


def test_invalid_agent_for_available_tools():

    selector = ToolSelector()

    with pytest.raises(
        ToolSelectionError
    ):

        selector.get_available_tools(
            "not-an-agent"
        )


def test_invalid_agent_for_select():

    selector = ToolSelector()

    with pytest.raises(
        ToolSelectionError
    ):

        selector.select(
            "not-an-agent",
            "calculator",
        )


def test_invalid_query_for_select():

    selector = ToolSelector()
    agent = create_agent()

    with pytest.raises(
        ToolSelectionError
    ):

        selector.select(
            agent,
            None,
        )