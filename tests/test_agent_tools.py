"""
Ultron Agent Tools Tests
Version: v0.39

Tests:
- AgentTool creation
- Tool validation
- Tool configuration
- Tool handler
- Tool execution
- Tool enable/disable
- Tool serialization
- Tool restoration
"""

import pytest

from modules.agent.tool import AgentTool
from modules.agent.tool_result import ToolResult


# ============================================================
# AgentTool Creation Tests
# ============================================================


def test_tool_creation():

    tool = AgentTool(
        name="calculator",
        description="Performs calculations",
    )

    assert tool.name == "calculator"
    assert tool.description == "Performs calculations"
    assert tool.enabled is True
    assert tool.config == {}
    assert tool.handler is None


def test_tool_name_is_trimmed():

    tool = AgentTool(
        name="  calculator  ",
    )

    assert tool.name == "calculator"


def test_tool_description_is_trimmed():

    tool = AgentTool(
        name="calculator",
        description="  Calculator tool  ",
    )

    assert tool.description == "Calculator tool"


def test_tool_default_enabled():

    tool = AgentTool(
        name="calculator",
    )

    assert tool.is_enabled() is True


# ============================================================
# Validation Tests
# ============================================================


def test_tool_requires_name():

    with pytest.raises(ValueError):

        AgentTool(
            name="",
        )


def test_tool_invalid_description():

    with pytest.raises(ValueError):

        AgentTool(
            name="calculator",
            description=123,
        )


def test_tool_invalid_config():

    with pytest.raises(ValueError):

        AgentTool(
            name="calculator",
            config="invalid",
        )


def test_tool_invalid_handler():

    with pytest.raises(ValueError):

        AgentTool(
            name="calculator",
            handler="not-callable",
        )


# ============================================================
# Configuration Tests
# ============================================================


def test_tool_config():

    tool = AgentTool(
        name="calculator",
        config={
            "precision": 2,
        },
    )

    assert tool.get_config(
        "precision"
    ) == 2


def test_tool_set_config():

    tool = AgentTool(
        name="calculator",
    )

    tool.set_config(
        {
            "precision": 4,
        }
    )

    assert tool.get_config(
        "precision"
    ) == 4


def test_tool_update_config():

    tool = AgentTool(
        name="calculator",
        config={
            "precision": 2,
        },
    )

    tool.update_config(
        rounding=True,
    )

    assert tool.get_config(
        "precision"
    ) == 2

    assert tool.get_config(
        "rounding"
    ) is True


def test_tool_get_complete_config():

    tool = AgentTool(
        name="calculator",
        config={
            "precision": 2,
            "rounding": True,
        },
    )

    config = tool.get_config()

    assert config == {
        "precision": 2,
        "rounding": True,
    }

    assert config is not tool.config


def test_tool_get_missing_config():

    tool = AgentTool(
        name="calculator",
    )

    assert tool.get_config(
        "missing",
        "default",
    ) == "default"


# ============================================================
# Handler Tests
# ============================================================


def test_tool_set_handler():

    tool = AgentTool(
        name="calculator",
    )

    def calculate(value):

        return value * 2

    tool.set_handler(
        calculate
    )

    assert tool.has_handler() is True


def test_tool_has_no_handler():

    tool = AgentTool(
        name="calculator",
    )

    assert tool.has_handler() is False


def test_tool_set_invalid_handler():

    tool = AgentTool(
        name="calculator",
    )

    with pytest.raises(ValueError):

        tool.set_handler(
            "not-callable"
        )


# ============================================================
# Tool Execution Tests
# ============================================================


def test_tool_execution():

    tool = AgentTool(
        name="calculator",
        handler=lambda value: value * 2,
    )

    result = tool.execute(
        value=5,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.result == 10
    assert result.error is None
    assert result.tool_name == "calculator"


def test_tool_execution_with_config():

    tool = AgentTool(
        name="calculator",
        config={
            "multiplier": 3,
        },
        handler=lambda value, multiplier: (
            value * multiplier
        ),
    )

    result = tool.execute(
        value=4,
    )

    assert result.success is True
    assert result.result == 12


def test_runtime_parameters_override_config():

    tool = AgentTool(
        name="calculator",
        config={
            "multiplier": 2,
        },
        handler=lambda value, multiplier: (
            value * multiplier
        ),
    )

    result = tool.execute(
        value=5,
        multiplier=4,
    )

    assert result.success is True
    assert result.result == 20


def test_tool_execution_failure():

    def failing_tool():

        raise RuntimeError(
            "Tool execution failed"
        )

    tool = AgentTool(
        name="failing",
        handler=failing_tool,
    )

    result = tool.execute()

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert (
        "Tool execution failed"
        in result.error
    )


def test_disabled_tool_execution():

    tool = AgentTool(
        name="calculator",
        handler=lambda: "success",
    )

    tool.disable()

    result = tool.execute()

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


def test_tool_without_handler():

    tool = AgentTool(
        name="calculator",
    )

    result = tool.execute()

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert result.result is None
    assert (
        "no handler"
        in result.error.lower()
    )


def test_tool_execution_result_timestamps():

    tool = AgentTool(
        name="calculator",
        handler=lambda: "success",
    )

    result = tool.execute()

    assert result.started_at is not None
    assert result.finished_at is not None


# ============================================================
# Enable / Disable Tests
# ============================================================


def test_tool_enable():

    tool = AgentTool(
        name="calculator",
    )

    tool.disable()

    assert tool.is_enabled() is False

    assert tool.enable() is True

    assert tool.is_enabled() is True


def test_tool_disable():

    tool = AgentTool(
        name="calculator",
    )

    assert tool.disable() is True

    assert tool.is_enabled() is False


# ============================================================
# Serialization Tests
# ============================================================


def test_tool_to_dict():

    tool = AgentTool(
        name="calculator",
        description="Calculator tool",
        enabled=True,
        config={
            "precision": 2,
        },
        handler=lambda: "result",
    )

    data = tool.to_dict()

    assert data == {
        "name": "calculator",
        "description": "Calculator tool",
        "enabled": True,
        "config": {
            "precision": 2,
        },
    }

    assert "handler" not in data


def test_tool_from_dict():

    data = {
        "name": "calculator",
        "description": "Calculator tool",
        "enabled": True,
        "config": {
            "precision": 2,
        },
    }

    tool = AgentTool.from_dict(
        data
    )

    assert tool.name == "calculator"
    assert tool.description == "Calculator tool"
    assert tool.enabled is True
    assert tool.config == {
        "precision": 2,
    }
    assert tool.handler is None


def test_tool_serialization_round_trip():

    original = AgentTool(
        name="calculator",
        description="Calculator",
        enabled=True,
        config={
            "precision": 4,
            "rounding": True,
        },
    )

    data = original.to_dict()

    restored = AgentTool.from_dict(
        data
    )

    assert restored.name == original.name
    assert restored.description == original.description
    assert restored.enabled == original.enabled
    assert restored.config == original.config


# ============================================================
# Representation Tests
# ============================================================


def test_tool_repr():

    tool = AgentTool(
        name="calculator",
    )

    representation = repr(
        tool
    )

    assert "AgentTool" in representation
    assert "calculator" in representation
    assert "enabled=True" in representation
    assert "has_handler=False" in representation