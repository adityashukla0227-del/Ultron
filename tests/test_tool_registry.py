"""
Ultron Tool Registry Tests
Version: v0.39

Tests:
- ToolRegistry creation
- Tool registration
- Duplicate registration
- Tool retrieval
- Tool availability
- Tool listing
- Enabled tool filtering
- Tool execution
- Safe tool execution
- Tool removal
- Registry clearing
- Registry count
- Registry representation
"""


import pytest

from modules.agent.tool import AgentTool
from modules.agent.tool_registry import (
    ToolRegistry,
    ToolRegistryError,
)
from modules.agent.tool_result import ToolResult


# ============================================================
# Registry Creation Tests
# ============================================================


def test_registry_creation():

    registry = ToolRegistry()

    assert registry.count() == 0
    assert len(registry) == 0
    assert registry.list_tools() == []
    assert registry.list_tool_names() == []


# ============================================================
# Registration Tests
# ============================================================


def test_registry_register_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    result = registry.register(
        tool
    )

    assert result is True
    assert registry.count() == 1
    assert registry.get(
        "calculator"
    ) is tool


def test_registry_register_multiple_tools():

    registry = ToolRegistry()

    calculator = AgentTool(
        name="calculator",
    )

    search = AgentTool(
        name="search",
    )

    assert registry.register(
        calculator
    ) is True

    assert registry.register(
        search
    ) is True

    assert registry.count() == 2


def test_registry_rejects_duplicate_tool():

    registry = ToolRegistry()

    first = AgentTool(
        name="calculator",
    )

    second = AgentTool(
        name="calculator",
    )

    assert registry.register(
        first
    ) is True

    assert registry.register(
        second
    ) is False

    assert registry.count() == 1
    assert registry.get(
        "calculator"
    ) is first


def test_registry_rejects_invalid_tool():

    registry = ToolRegistry()

    with pytest.raises(
        ToolRegistryError
    ):

        registry.register(
            "not-a-tool"
        )


# ============================================================
# Retrieval Tests
# ============================================================


def test_registry_get_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    registry.register(
        tool
    )

    assert registry.get(
        "calculator"
    ) is tool


def test_registry_get_missing_tool():

    registry = ToolRegistry()

    assert registry.get(
        "missing"
    ) is None


def test_registry_get_trims_tool_name():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    registry.register(
        tool
    )

    assert registry.get(
        "  calculator  "
    ) is tool


# ============================================================
# Availability Tests
# ============================================================


def test_registry_has_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    registry.register(
        tool
    )

    assert registry.has(
        "calculator"
    ) is True


def test_registry_missing_tool():

    registry = ToolRegistry()

    assert registry.has(
        "missing"
    ) is False


def test_registry_contains_operator():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    registry.register(
        tool
    )

    assert "calculator" in registry
    assert "missing" not in registry


# ============================================================
# Listing Tests
# ============================================================


def test_registry_list_tools():

    registry = ToolRegistry()

    first = AgentTool(
        name="calculator",
    )

    second = AgentTool(
        name="search",
    )

    registry.register(first)
    registry.register(second)

    tools = registry.list_tools()

    assert len(tools) == 2
    assert first in tools
    assert second in tools


def test_registry_list_tool_names():

    registry = ToolRegistry()

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    registry.register(
        AgentTool(
            name="search",
        )
    )

    names = registry.list_tool_names()

    assert "calculator" in names
    assert "search" in names
    assert len(names) == 2


# ============================================================
# Enabled Tool Tests
# ============================================================


def test_registry_get_enabled_tools():

    registry = ToolRegistry()

    enabled_tool = AgentTool(
        name="calculator",
    )

    disabled_tool = AgentTool(
        name="search",
    )

    disabled_tool.disable()

    registry.register(
        enabled_tool
    )

    registry.register(
        disabled_tool
    )

    enabled_tools = (
        registry.get_enabled_tools()
    )

    assert enabled_tool in enabled_tools
    assert disabled_tool not in enabled_tools
    assert len(enabled_tools) == 1


# ============================================================
# Execution Tests
# ============================================================


def test_registry_execute_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
        handler=lambda value: value * 2,
    )

    registry.register(
        tool
    )

    result = registry.execute(
        "calculator",
        value=5,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.result == 10
    assert result.tool_name == "calculator"


def test_registry_execute_with_parameters():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
        config={
            "multiplier": 3,
        },
        handler=lambda value, multiplier: (
            value * multiplier
        ),
    )

    registry.register(
        tool
    )

    result = registry.execute(
        "calculator",
        value=4,
    )

    assert result.success is True
    assert result.result == 12


def test_registry_execute_runtime_override():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
        config={
            "multiplier": 2,
        },
        handler=lambda value, multiplier: (
            value * multiplier
        ),
    )

    registry.register(
        tool
    )

    result = registry.execute(
        "calculator",
        value=5,
        multiplier=4,
    )

    assert result.success is True
    assert result.result == 20


def test_registry_execute_missing_tool():

    registry = ToolRegistry()

    with pytest.raises(
        ToolRegistryError
    ):

        registry.execute(
            "missing"
        )


# ============================================================
# Safe Execution Tests
# ============================================================


def test_registry_execute_safe_success():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
        handler=lambda value: value * 2,
    )

    registry.register(
        tool
    )

    result = registry.execute_safe(
        "calculator",
        value=5,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.result == 10
    assert result.error is None


def test_registry_execute_safe_missing_tool():

    registry = ToolRegistry()

    result = registry.execute_safe(
        "missing"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert (
        "not registered"
        in result.error.lower()
    )


def test_registry_execute_safe_failure():

    registry = ToolRegistry()

    def failing_tool():

        raise RuntimeError(
            "Registry tool failed"
        )

    tool = AgentTool(
        name="failing",
        handler=failing_tool,
    )

    registry.register(
        tool
    )

    result = registry.execute_safe(
        "failing"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert (
        "Registry tool failed"
        in result.error
    )


def test_registry_execute_safe_disabled_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
        handler=lambda: "success",
    )

    tool.disable()

    registry.register(
        tool
    )

    result = registry.execute_safe(
        "calculator"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert (
        "disabled"
        in result.error.lower()
    )


# ============================================================
# Removal Tests
# ============================================================


def test_registry_unregister_tool():

    registry = ToolRegistry()

    tool = AgentTool(
        name="calculator",
    )

    registry.register(
        tool
    )

    assert registry.unregister(
        "calculator"
    ) is True

    assert registry.get(
        "calculator"
    ) is None

    assert registry.count() == 0


def test_registry_unregister_missing_tool():

    registry = ToolRegistry()

    assert registry.unregister(
        "missing"
    ) is False


def test_registry_remove_trims_name():

    registry = ToolRegistry()

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    assert registry.unregister(
        "  calculator  "
    ) is True

    assert registry.has(
        "calculator"
    ) is False


def test_registry_remove_invalid_name():

    registry = ToolRegistry()

    with pytest.raises(
        ToolRegistryError
    ):

        registry.unregister(
            123
        )


# ============================================================
# Clear Tests
# ============================================================


def test_registry_clear():

    registry = ToolRegistry()

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    registry.register(
        AgentTool(
            name="search",
        )
    )

    assert registry.count() == 2

    registry.clear()

    assert registry.count() == 0
    assert len(registry) == 0
    assert registry.list_tools() == []
    assert registry.list_tool_names() == []


# ============================================================
# Utility Tests
# ============================================================


def test_registry_count():

    registry = ToolRegistry()

    assert registry.count() == 0

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    assert registry.count() == 1

    registry.register(
        AgentTool(
            name="search",
        )
    )

    assert registry.count() == 2


def test_registry_len():

    registry = ToolRegistry()

    assert len(registry) == 0

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    assert len(registry) == 1


def test_registry_repr():

    registry = ToolRegistry()

    registry.register(
        AgentTool(
            name="calculator",
        )
    )

    registry.register(
        AgentTool(
            name="search",
        )
    )

    representation = repr(
        registry
    )

    assert "ToolRegistry" in representation
    assert "calculator" in representation
    assert "search" in representation