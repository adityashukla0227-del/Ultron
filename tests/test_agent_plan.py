"""
Ultron Agent Plan Tests
Version: v0.40

Tests:
- AgentPlan creation
- Validation
- Step management
- Selected tool management
- Status management
- Completion state
- Serialization
- Restoration
- Invalid input handling
- Representation
"""

import pytest

from modules.agent.agent_plan import (
    AgentPlan,
    AgentPlanValidationError,
)


# ============================================================
# Fixtures
# ============================================================


def create_plan():
    """
    Create a standard AgentPlan for testing.
    """

    return AgentPlan(
        agent_id="agent-001",
        query="Get the weather and search for information",
    )


# ============================================================
# Creation Tests
# ============================================================


def test_agent_plan_creation():

    plan = create_plan()

    assert plan is not None
    assert plan.agent_id == "agent-001"
    assert plan.query == (
        "Get the weather and search for information"
    )
    assert plan.status == "draft"
    assert plan.steps == []
    assert plan.selected_tools == []


def test_agent_plan_generates_id():

    plan = create_plan()

    assert isinstance(
        plan.id,
        str,
    )

    assert plan.id.strip()


def test_agent_plan_custom_id():

    plan = AgentPlan(
        agent_id="agent-001",
        query="Test query",
        plan_id="plan-123",
    )

    assert plan.id == "plan-123"


def test_agent_plan_repr():

    plan = create_plan()

    representation = repr(
        plan
    )

    assert "AgentPlan" in representation
    assert "agent-001" in representation
    assert "draft" in representation


# ============================================================
# Validation Tests
# ============================================================


def test_agent_plan_validate():

    plan = create_plan()

    assert plan.validate() is True


def test_agent_plan_requires_agent_id():

    with pytest.raises(
        AgentPlanValidationError
    ):

        AgentPlan(
            agent_id="",
            query="Test query",
        )


def test_agent_plan_requires_query():

    with pytest.raises(
        AgentPlanValidationError
    ):

        AgentPlan(
            agent_id="agent-001",
            query="",
        )


def test_agent_plan_invalid_status():

    with pytest.raises(
        AgentPlanValidationError
    ):

        AgentPlan(
            agent_id="agent-001",
            query="Test query",
            status="invalid",
        )


def test_agent_plan_invalid_step():

    with pytest.raises(
        AgentPlanValidationError
    ):

        AgentPlan(
            agent_id="agent-001",
            query="Test query",
            steps=[
                "invalid-step"
            ],
        )


# ============================================================
# Step Management Tests
# ============================================================


def test_add_step():

    plan = create_plan()

    result = plan.add_step(
        {
            "action": "get_weather",
            "tool": "weather",
        }
    )

    assert result is True
    assert len(plan.steps) == 1


def test_add_duplicate_step():

    plan = create_plan()

    step = {
        "action": "get_weather",
        "tool": "weather",
    }

    assert plan.add_step(
        step
    ) is True

    assert plan.add_step(
        step
    ) is False

    assert len(plan.steps) == 1


def test_add_invalid_step():

    plan = create_plan()

    with pytest.raises(
        AgentPlanValidationError
    ):

        plan.add_step(
            "invalid"
        )


def test_get_step():

    plan = create_plan()

    plan.add_step(
        {
            "action": "search",
            "tool": "search",
        }
    )

    step = plan.get_step(
        0
    )

    assert step is not None
    assert step["action"] == "search"
    assert step["tool"] == "search"


def test_get_missing_step():

    plan = create_plan()

    assert plan.get_step(
        0
    ) is None


def test_get_steps_returns_copy():

    plan = create_plan()

    plan.add_step(
        {
            "action": "search",
        }
    )

    steps = plan.get_steps()

    assert steps == plan.steps

    steps.append(
        {
            "action": "another",
        }
    )

    assert len(
        plan.steps
    ) == 1


def test_remove_step():

    plan = create_plan()

    plan.add_step(
        {
            "action": "search",
        }
    )

    assert plan.remove_step(
        0
    ) is True

    assert plan.steps == []


def test_remove_missing_step():

    plan = create_plan()

    assert plan.remove_step(
        0
    ) is False


def test_remove_step_invalid_index():

    plan = create_plan()

    with pytest.raises(
        AgentPlanValidationError
    ):

        plan.remove_step(
            "0"
        )


# ============================================================
# Selected Tool Tests
# ============================================================


def test_add_selected_tool():

    plan = create_plan()

    result = plan.add_selected_tool(
        "weather"
    )

    assert result is True
    assert plan.selected_tools == [
        "weather"
    ]


def test_add_duplicate_selected_tool():

    plan = create_plan()

    assert plan.add_selected_tool(
        "weather"
    ) is True

    assert plan.add_selected_tool(
        "weather"
    ) is False

    assert plan.selected_tools == [
        "weather"
    ]


def test_add_selected_tool_strips_whitespace():

    plan = create_plan()

    assert plan.add_selected_tool(
        " weather "
    ) is True

    assert plan.selected_tools == [
        "weather"
    ]


def test_add_invalid_selected_tool():

    plan = create_plan()

    with pytest.raises(
        AgentPlanValidationError
    ):

        plan.add_selected_tool(
            ""
        )


def test_remove_selected_tool():

    plan = create_plan()

    plan.add_selected_tool(
        "weather"
    )

    assert plan.remove_selected_tool(
        "weather"
    ) is True

    assert plan.selected_tools == []


def test_remove_missing_selected_tool():

    plan = create_plan()

    assert plan.remove_selected_tool(
        "weather"
    ) is False


def test_has_selected_tool():

    plan = create_plan()

    plan.add_selected_tool(
        "weather"
    )

    assert plan.has_selected_tool(
        "weather"
    ) is True

    assert plan.has_selected_tool(
        "search"
    ) is False


def test_get_selected_tools():

    plan = create_plan()

    plan.add_selected_tool(
        "weather"
    )

    plan.add_selected_tool(
        "search"
    )

    tools = plan.get_selected_tools()

    assert tools == [
        "weather",
        "search",
    ]


# ============================================================
# Status Tests
# ============================================================


def test_set_status():

    plan = create_plan()

    plan.set_status(
        "planned"
    )

    assert plan.status == "planned"


def test_set_invalid_status():

    plan = create_plan()

    with pytest.raises(
        AgentPlanValidationError
    ):

        plan.set_status(
            "unknown"
        )


def test_mark_planned():

    plan = create_plan()

    assert plan.mark_planned() is True
    assert plan.status == "planned"
    assert plan.is_ready() is True


def test_mark_executing():

    plan = create_plan()

    plan.mark_executing()

    assert plan.status == "executing"


def test_mark_completed():

    plan = create_plan()

    plan.mark_completed()

    assert plan.status == "completed"
    assert plan.is_finished() is True


def test_mark_failed():

    plan = create_plan()

    plan.mark_failed()

    assert plan.status == "failed"
    assert plan.is_finished() is True


def test_cancel_plan():

    plan = create_plan()

    plan.cancel()

    assert plan.status == "cancelled"
    assert plan.is_finished() is True


def test_draft_plan_is_not_ready():

    plan = create_plan()

    assert plan.is_ready() is False


def test_executing_plan_is_not_finished():

    plan = create_plan()

    plan.mark_executing()

    assert plan.is_finished() is False


# ============================================================
# Serialization Tests
# ============================================================


def test_to_dict():

    plan = create_plan()

    plan.add_step(
        {
            "action": "get_weather",
            "tool": "weather",
        }
    )

    plan.add_selected_tool(
        "weather"
    )

    plan.mark_planned()

    data = plan.to_dict()

    assert data["id"] == plan.id
    assert data["agent_id"] == "agent-001"
    assert data["query"] == (
        "Get the weather and search for information"
    )
    assert data["status"] == "planned"
    assert data["selected_tools"] == [
        "weather"
    ]
    assert len(
        data["steps"]
    ) == 1


def test_from_dict():

    data = {
        "id": "plan-001",
        "agent_id": "agent-001",
        "query": "Search for information",
        "steps": [
            {
                "action": "search",
                "tool": "search",
            }
        ],
        "selected_tools": [
            "search"
        ],
        "status": "planned",
        "created_at": "2026-08-21T10:00:00",
    }

    plan = AgentPlan.from_dict(
        data
    )

    assert plan.id == "plan-001"
    assert plan.agent_id == "agent-001"
    assert plan.query == (
        "Search for information"
    )
    assert plan.status == "planned"
    assert plan.selected_tools == [
        "search"
    ]
    assert len(
        plan.steps
    ) == 1


def test_serialization_round_trip():

    plan = create_plan()

    plan.add_step(
        {
            "action": "weather",
            "tool": "weather",
            "parameters": {
                "city": "Lucknow",
            },
        }
    )

    plan.add_selected_tool(
        "weather"
    )

    plan.mark_planned()

    restored = AgentPlan.from_dict(
        plan.to_dict()
    )

    assert restored.id == plan.id
    assert restored.agent_id == plan.agent_id
    assert restored.query == plan.query
    assert restored.steps == plan.steps
    assert restored.selected_tools == plan.selected_tools
    assert restored.status == plan.status
    assert restored.created_at == plan.created_at


def test_from_dict_invalid_data():

    with pytest.raises(
        AgentPlanValidationError
    ):

        AgentPlan.from_dict(
            "invalid"
        )