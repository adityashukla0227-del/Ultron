"""
Tests for Ultron Agent Runtime Context.

Version: v0.49
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_runtime_context import (
    AgentRuntimeContext,
    AgentRuntimeContextError,
)


def create_agent() -> Agent:
    return Agent(
        name="Test Agent",
        description="Runtime context test agent",
        action="test_action",
    )


# ============================================================
# Construction
# ============================================================


def test_runtime_context_creation():
    agent = create_agent()

    context = AgentRuntimeContext(
        agent=agent,
        query="Hello Ultron",
    )

    assert context.agent is agent
    assert context.query == "Hello Ultron"
    assert context.status == "created"
    assert context.id
    assert context.created_at


def test_runtime_context_default_collections_are_independent():
    agent = create_agent()

    context_a = AgentRuntimeContext(agent=agent)
    context_b = AgentRuntimeContext(agent=agent)

    context_a.session["key"] = "value"
    context_a.memory["key"] = "value"
    context_a.state["key"] = "value"

    assert context_b.session == {}
    assert context_b.memory == {}
    assert context_b.state == {}


def test_runtime_context_requires_agent():
    with pytest.raises(AgentRuntimeContextError):
        AgentRuntimeContext(
            agent="invalid",
        )


# ============================================================
# Validation
# ============================================================


def test_runtime_context_validation():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    assert context.validate() is True


def test_invalid_status_is_rejected():
    with pytest.raises(AgentRuntimeContextError):
        AgentRuntimeContext(
            agent=create_agent(),
            status="invalid",
        )


# ============================================================
# Query
# ============================================================


def test_query_is_normalized():
    context = AgentRuntimeContext(
        agent=create_agent(),
        query="  hello world  ",
    )

    assert context.query == "hello world"


def test_set_query():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_query("  new query  ")

    assert context.get_query() == "new query"


def test_set_query_requires_string():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    with pytest.raises(AgentRuntimeContextError):
        context.set_query(123)


# ============================================================
# Session
# ============================================================


def test_session_values():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_session_value(
        "user_id",
        "user-123",
    )

    assert (
        context.get_session_value("user_id")
        == "user-123"
    )


def test_session_default():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    assert (
        context.get_session_value(
            "missing",
            "default",
        )
        == "default"
    )


def test_remove_session_value():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_session_value(
        "key",
        "value",
    )

    assert context.remove_session_value("key")
    assert context.get_session_value("key") is None
    assert not context.remove_session_value("key")


# ============================================================
# Memory
# ============================================================


def test_memory_values():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_memory_value(
        "topic",
        "AI",
    )

    assert (
        context.get_memory_value("topic")
        == "AI"
    )


def test_remove_memory_value():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_memory_value(
        "topic",
        "AI",
    )

    assert context.remove_memory_value("topic")
    assert context.get_memory_value("topic") is None


# ============================================================
# State
# ============================================================


def test_state_values():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_state(
        "step",
        1,
    )

    assert context.get_state("step") == 1


def test_remove_state():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_state(
        "step",
        1,
    )

    assert context.remove_state("step")
    assert context.get_state("step") is None


# ============================================================
# Permissions
# ============================================================


def test_permissions():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_permission(
        "web.search",
        True,
    )

    assert context.get_permission(
        "web.search"
    ) is True

    assert context.has_permission(
        "web.search"
    )


def test_missing_permission_is_false():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    assert not context.has_permission(
        "camera.access"
    )


# ============================================================
# Metadata
# ============================================================


def test_metadata_values():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_metadata(
        "source",
        "api",
    )

    assert (
        context.get_metadata("source")
        == "api"
    )


# ============================================================
# Execution
# ============================================================


def test_execution_values():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_execution_value(
        "attempt",
        1,
    )

    assert (
        context.get_execution_value("attempt")
        == 1
    )


# ============================================================
# Plan
# ============================================================


def test_plan_management():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    plan = {
        "id": "plan-1",
        "steps": [],
    }

    context.set_plan(plan)

    assert context.get_plan() == plan


# ============================================================
# Status
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        "created",
        "ready",
        "planning",
        "planned",
        "executing",
        "waiting",
        "resuming",
        "completed",
        "failed",
        "cancelled",
    ],
)
def test_valid_statuses(status):
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_status(status)

    assert context.status == status


def test_status_is_normalized():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_status("  EXECUTING  ")

    assert context.status == "executing"


def test_terminal_status():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_status("completed")

    assert context.is_terminal()


def test_non_terminal_status():
    context = AgentRuntimeContext(
        agent=create_agent()
    )

    context.set_status("executing")

    assert not context.is_terminal()


# ============================================================
# Serialization
# ============================================================


def test_to_dict():
    agent = create_agent()

    context = AgentRuntimeContext(
        agent=agent,
        query="test query",
        session={"session_id": "s1"},
        memory={"topic": "AI"},
        state={"step": 1},
        permissions={"web.search": True},
        metadata={"source": "test"},
        execution={"attempt": 1},
    )

    data = context.to_dict()

    assert data["id"] == context.id
    assert data["query"] == "test query"
    assert data["agent"]["name"] == "Test Agent"
    assert data["session"]["session_id"] == "s1"
    assert data["memory"]["topic"] == "AI"
    assert data["state"]["step"] == 1
    assert data["permissions"]["web.search"] is True
    assert data["metadata"]["source"] == "test"
    assert data["execution"]["attempt"] == 1


def test_from_dict():
    agent = create_agent()

    context = AgentRuntimeContext(
        agent=agent,
        query="test query",
        session={"session_id": "s1"},
        memory={"topic": "AI"},
        state={"step": 1},
        permissions={"web.search": True},
        metadata={"source": "test"},
        execution={"attempt": 1},
    )

    data = context.to_dict()

    restored = AgentRuntimeContext.from_dict(
        data
    )

    assert restored.id == context.id
    assert restored.query == context.query
    assert restored.agent.name == context.agent.name
    assert restored.session == context.session
    assert restored.memory == context.memory
    assert restored.state == context.state
    assert restored.permissions == context.permissions
    assert restored.metadata == context.metadata
    assert restored.execution == context.execution
    assert restored.status == context.status


# ============================================================
# Representation
# ============================================================


def test_repr():
    context = AgentRuntimeContext(
        agent=create_agent(),
        query="test",
    )

    representation = repr(context)

    assert "AgentRuntimeContext" in representation
    assert context.id in representation
    assert "Test Agent" in representation