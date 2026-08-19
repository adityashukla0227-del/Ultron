"""
Ultron Agent System Tests
Version: v0.37

Tests:
- Agent creation
- Agent validation
- Agent enable/disable
- Agent parameters
- Agent registry
- Agent engine
- Action registration
- Agent execution
- Runtime parameter override
- Safe execution
- Execution failure handling
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import (
    AgentEngine,
    AgentEngineError,
    AgentExecutionError,
)
from modules.agent.agent_registry import AgentRegistry


# ============================================================
# Agent Tests
# ============================================================


def test_agent_creation():

    agent = Agent(
        name="Test Agent",
        description="A test agent",
        action="hello",
    )

    assert agent.id is not None
    assert agent.name == "Test Agent"
    assert agent.description == "A test agent"
    assert agent.action == "hello"
    assert agent.enabled is True


def test_agent_default_parameters():

    agent = Agent(
        name="Parameter Agent",
        action="hello",
    )

    assert agent.parameters == {}


def test_agent_custom_parameters():

    agent = Agent(
        name="Parameter Agent",
        action="echo",
        parameters={
            "message": "Ultron",
        },
    )

    assert agent.parameters["message"] == "Ultron"


def test_agent_validation():

    agent = Agent(
        name="Valid Agent",
        action="hello",
    )

    assert agent.validate() is True


def test_agent_active_by_default():

    agent = Agent(
        name="Active Agent",
        action="hello",
    )

    assert agent.is_active() is True


def test_agent_disable():

    agent = Agent(
        name="Disabled Agent",
        action="hello",
    )

    assert agent.disable() is True
    assert agent.is_active() is False


def test_agent_enable():

    agent = Agent(
        name="Enable Agent",
        action="hello",
    )

    agent.disable()

    assert agent.enable() is True
    assert agent.is_active() is True


# ============================================================
# Registry Tests
# ============================================================


def test_registry_register():

    registry = AgentRegistry()

    agent = Agent(
        name="Registry Agent",
        action="hello",
    )

    result = registry.register(
        agent
    )

    assert result is True
    assert registry.get(
        agent.id
    ) is agent


def test_registry_get_missing():

    registry = AgentRegistry()

    assert registry.get(
        "missing-agent-id"
    ) is None


def test_registry_list():

    registry = AgentRegistry()

    first = Agent(
        name="First",
        action="hello",
    )

    second = Agent(
        name="Second",
        action="hello",
    )

    registry.register(first)
    registry.register(second)

    agents = registry.list()

    ids = [
        agent.id
        for agent in agents
    ]

    assert first.id in ids
    assert second.id in ids
    assert len(agents) == 2


def test_registry_remove():

    registry = AgentRegistry()

    agent = Agent(
        name="Remove Agent",
        action="hello",
    )

    registry.register(agent)

    assert registry.remove(
        agent.id
    ) is True

    assert registry.get(
        agent.id
    ) is None


# ============================================================
# Engine Action Tests
# ============================================================


def test_engine_register_action():

    engine = AgentEngine()

    result = engine.register_action(
        "hello",
        lambda: "Hello from Agent",
    )

    assert result is True
    assert engine.has_action(
        "hello"
    ) is True


def test_engine_get_action():

    engine = AgentEngine()

    handler = lambda: "Hello"

    engine.register_action(
        "hello",
        handler,
    )

    assert engine.get_action(
        "hello"
    ) is handler


def test_engine_remove_action():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    assert engine.remove_action(
        "hello"
    ) is True

    assert engine.has_action(
        "hello"
    ) is False


def test_engine_list_actions():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    engine.register_action(
        "echo",
        lambda message: message,
    )

    actions = engine.list_actions()

    assert "hello" in actions
    assert "echo" in actions
    assert len(actions) == 2


# ============================================================
# Engine Execution Tests
# ============================================================


def test_engine_execute_agent():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello from Ultron Agent",
    )

    agent = Agent(
        name="Hello Agent",
        action="hello",
    )

    result = engine.execute(
        agent
    )

    assert result == (
        "Hello from Ultron Agent"
    )

    assert agent.last_run is not None


def test_engine_execute_with_parameters():

    engine = AgentEngine()

    engine.register_action(
        "echo",
        lambda message: message,
    )

    agent = Agent(
        name="Echo Agent",
        action="echo",
        parameters={
            "message": "Ultron",
        },
    )

    result = engine.execute(
        agent
    )

    assert result == "Ultron"


def test_engine_runtime_parameter_override():

    engine = AgentEngine()

    engine.register_action(
        "echo",
        lambda message: message,
    )

    agent = Agent(
        name="Override Agent",
        action="echo",
        parameters={
            "message": "Original",
        },
    )

    result = engine.execute(
        agent,
        message="Runtime",
    )

    assert result == "Runtime"


def test_engine_execute_by_id():

    engine = AgentEngine()

    registry = AgentRegistry()

    engine.register_action(
        "hello",
        lambda: "Executed by ID",
    )

    agent = Agent(
        name="ID Agent",
        action="hello",
    )

    registry.register(agent)

    result = engine.execute_by_id(
        agent.id,
        registry,
    )

    assert result == "Executed by ID"


# ============================================================
# Safe Execution Tests
# ============================================================


def test_engine_execute_safe_success():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Success",
    )

    agent = Agent(
        name="Safe Agent",
        action="hello",
    )

    result = engine.execute_safe(
        agent
    )

    assert result["success"] is True
    assert result["agent_id"] == agent.id
    assert result["result"] == "Success"
    assert result["error"] is None


def test_engine_execute_safe_failure():

    engine = AgentEngine()

    def failing_action():

        raise RuntimeError(
            "Something went wrong"
        )

    engine.register_action(
        "fail",
        failing_action,
    )

    agent = Agent(
        name="Failing Agent",
        action="fail",
    )

    result = engine.execute_safe(
        agent
    )

    assert result["success"] is False
    assert result["agent_id"] == agent.id
    assert result["result"] is None
    assert (
        "Something went wrong"
        in result["error"]
    )


# ============================================================
# Error Handling Tests
# ============================================================


def test_engine_unknown_action():

    engine = AgentEngine()

    agent = Agent(
        name="Unknown Action Agent",
        action="unknown",
    )

    with pytest.raises(
        AgentExecutionError
    ):

        engine.execute(
            agent
        )


def test_engine_disabled_agent():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    agent = Agent(
        name="Disabled Agent",
        action="hello",
    )

    agent.disable()

    with pytest.raises(
        AgentExecutionError
    ):

        engine.execute(
            agent
        )


def test_engine_invalid_agent():

    engine = AgentEngine()

    with pytest.raises(
        AgentExecutionError
    ):

        engine.execute(
            "not-an-agent"
        )


def test_engine_invalid_action_name():

    engine = AgentEngine()

    with pytest.raises(
        AgentEngineError
    ):

        engine.register_action(
            "",
            lambda: "Hello",
        )


def test_engine_invalid_action_handler():

    engine = AgentEngine()

    with pytest.raises(
        AgentEngineError
    ):

        engine.register_action(
            "hello",
            "not-callable",
        )


# ============================================================
# Engine Utility Tests
# ============================================================


def test_engine_length():

    engine = AgentEngine()

    assert len(engine) == 0

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    assert len(engine) == 1


def test_engine_clear_actions():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    engine.register_action(
        "echo",
        lambda message: message,
    )

    assert len(engine) == 2

    engine.clear_actions()

    assert len(engine) == 0


def test_engine_repr():

    engine = AgentEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    representation = repr(
        engine
    )

    assert "AgentEngine" in representation
    assert "actions=1" in representation