"""
Ultron Agent Planner Tests
Version: v0.40

Tests:
- AgentPlanStep creation
- AgentPlanStep validation
- Step lifecycle management
- Step state queries
- Step serialization/restoration
- AgentPlan creation
- Plan step management
- Step ordering
- Plan lifecycle
- Plan progress tracking
- Plan serialization/restoration
- AgentPlanner creation
- Plan creation
- Step creation
- Plan validation
- Next-step resolution
- Invalid input handling
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanError,
    AgentPlanner,
    AgentPlanStep,
)


# ============================================================
# Fixtures
# ============================================================


def create_agent():
    """
    Create a test agent.
    """

    return Agent(
        name="Planner Agent",
        description="Agent used for planner tests.",
        action="test",
    )


def create_step(
    action="test_action",
    description="Test step",
    parameters=None,
    tool_name=None,
):
    """
    Create a test plan step.
    """

    return AgentPlanStep(
        action=action,
        description=description,
        parameters=parameters,
        tool_name=tool_name,
    )


def create_plan():
    """
    Create a test plan.
    """

    agent = create_agent()

    return AgentPlan(
        agent=agent,
        name="Test Plan",
        description="Test execution plan.",
    )


# ============================================================
# AgentPlanStep Creation Tests
# ============================================================


def test_plan_step_creation():

    step = create_step()

    assert step is not None
    assert step.action == "test_action"
    assert step.description == "Test step"
    assert step.status == "pending"


def test_plan_step_generates_id():

    step = create_step()

    assert isinstance(
        step.id,
        str,
    )

    assert step.id


def test_plan_step_parameters():

    step = create_step(
        parameters={
            "value": 10,
            "mode": "test",
        }
    )

    assert step.parameters == {
        "value": 10,
        "mode": "test",
    }


def test_plan_step_tool_name():

    step = create_step(
        tool_name="calculator"
    )

    assert step.tool_name == "calculator"


def test_plan_step_default_result_and_error():

    step = create_step()

    assert step.result is None
    assert step.error is None


# ============================================================
# AgentPlanStep Validation Tests
# ============================================================


def test_plan_step_requires_action():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep(
            action=""
        )


def test_plan_step_invalid_action():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep(
            action=None
        )


def test_plan_step_invalid_parameters():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep(
            action="test",
            parameters="invalid",
        )


def test_plan_step_invalid_status():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep(
            action="test",
            status="invalid",
        )


def test_plan_step_invalid_tool_name():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep(
            action="test",
            tool_name="",
        )


# ============================================================
# AgentPlanStep Lifecycle Tests
# ============================================================


def test_plan_step_start():

    step = create_step()

    result = step.start()

    assert result is True
    assert step.status == "running"


def test_plan_step_complete():

    step = create_step()

    step.start()

    result = step.complete(
        result="success"
    )

    assert result is True
    assert step.status == "completed"
    assert step.result == "success"
    assert step.error is None


def test_plan_step_fail():

    step = create_step()

    step.start()

    result = step.fail(
        "Something went wrong"
    )

    assert result is True
    assert step.status == "failed"
    assert step.error == "Something went wrong"


def test_plan_step_skip():

    step = create_step()

    result = step.skip()

    assert result is True
    assert step.status == "skipped"


def test_plan_step_reset():

    step = create_step()

    step.start()

    step.complete(
        "done"
    )

    result = step.reset()

    assert result is True
    assert step.status == "pending"
    assert step.result is None
    assert step.error is None


def test_plan_step_start_after_completed():

    step = create_step()

    step.start()
    step.complete()

    result = step.start()

    assert result is False
    assert step.status == "completed"


def test_plan_step_start_after_failed():

    step = create_step()

    step.start()

    step.fail(
        "failure"
    )

    result = step.start()

    assert result is True
    assert step.status == "running"


# ============================================================
# AgentPlanStep State Tests
# ============================================================


def test_plan_step_is_pending():

    step = create_step()

    assert step.is_pending() is True
    assert step.is_running() is False


def test_plan_step_is_running():

    step = create_step()

    step.start()

    assert step.is_running() is True


def test_plan_step_is_completed():

    step = create_step()

    step.start()
    step.complete()

    assert step.is_completed() is True
    assert step.is_finished() is True


def test_plan_step_is_failed():

    step = create_step()

    step.start()
    step.fail(
        "failure"
    )

    assert step.is_failed() is True
    assert step.is_finished() is True


def test_plan_step_is_skipped():

    step = create_step()

    step.skip()

    assert step.is_skipped() is True
    assert step.is_finished() is True


# ============================================================
# AgentPlanStep Serialization Tests
# ============================================================


def test_plan_step_to_dict():

    step = create_step(
        parameters={
            "value": 10,
        },
        tool_name="calculator",
    )

    data = step.to_dict()

    assert data["id"] == step.id
    assert data["action"] == "test_action"
    assert data["description"] == "Test step"
    assert data["parameters"] == {
        "value": 10,
    }
    assert data["tool_name"] == "calculator"
    assert data["status"] == "pending"


def test_plan_step_from_dict():

    original = create_step(
        parameters={
            "value": 25,
        },
        tool_name="calculator",
    )

    data = original.to_dict()

    restored = AgentPlanStep.from_dict(
        data
    )

    assert restored.id == original.id
    assert restored.action == original.action
    assert restored.description == original.description
    assert restored.parameters == original.parameters
    assert restored.tool_name == original.tool_name
    assert restored.status == original.status


def test_plan_step_from_invalid_dict():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlanStep.from_dict(
            "invalid"
        )


def test_plan_step_repr():

    step = create_step()

    representation = repr(
        step
    )

    assert "AgentPlanStep" in representation
    assert step.id in representation


# ============================================================
# AgentPlan Creation Tests
# ============================================================


def test_plan_creation():

    agent = create_agent()

    plan = AgentPlan(
        agent=agent,
        name="Test Plan",
        description="Test plan.",
    )

    assert plan is not None
    assert plan.agent_id == agent.id
    assert plan.name == "Test Plan"
    assert plan.description == "Test plan."
    assert plan.status == "draft"
    assert plan.steps == []


def test_plan_generates_id():

    plan = create_plan()

    assert isinstance(
        plan.id,
        str,
    )

    assert plan.id


def test_plan_requires_agent():

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlan(
            agent="invalid"
        )


def test_plan_invalid_status():

    agent = create_agent()

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlan(
            agent=agent,
            status="invalid",
        )


# ============================================================
# AgentPlan Step Management Tests
# ============================================================


def test_add_step():

    plan = create_plan()
    step = create_step()

    result = plan.add_step(
        step
    )

    assert result is True
    assert len(plan.steps) == 1
    assert plan.steps[0] is step


def test_add_duplicate_step():

    plan = create_plan()
    step = create_step()

    plan.add_step(
        step
    )

    result = plan.add_step(
        step
    )

    assert result is False
    assert len(plan.steps) == 1


def test_add_invalid_step():

    plan = create_plan()

    with pytest.raises(
        AgentPlanError
    ):

        plan.add_step(
            "invalid"
        )


def test_insert_step():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    plan.add_step(
        first
    )

    result = plan.insert_step(
        0,
        second,
    )

    assert result is True
    assert plan.steps[0].action == "second"
    assert plan.steps[1].action == "first"


def test_insert_step_invalid_index():

    plan = create_plan()
    step = create_step()

    with pytest.raises(
        AgentPlanError
    ):

        plan.insert_step(
            5,
            step,
        )


def test_remove_step():

    plan = create_plan()
    step = create_step()

    plan.add_step(
        step
    )

    result = plan.remove_step(
        step.id
    )

    assert result is True
    assert len(plan.steps) == 0


def test_remove_missing_step():

    plan = create_plan()

    result = plan.remove_step(
        "missing"
    )

    assert result is False


def test_get_step():

    plan = create_plan()
    step = create_step()

    plan.add_step(
        step
    )

    result = plan.get_step(
        step.id
    )

    assert result is step


def test_get_missing_step():

    plan = create_plan()

    result = plan.get_step(
        "missing"
    )

    assert result is None


def test_get_step_by_index():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    plan.add_step(
        first
    )

    plan.add_step(
        second
    )

    assert plan.get_step_by_index(
        0
    ) is first

    assert plan.get_step_by_index(
        1
    ) is second


def test_get_step_by_invalid_index():

    plan = create_plan()

    assert plan.get_step_by_index(
        0
    ) is None


def test_list_steps():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    plan.add_step(
        first
    )

    plan.add_step(
        second
    )

    steps = plan.list_steps()

    assert steps == [
        first,
        second,
    ]


def test_clear_steps():

    plan = create_plan()

    plan.add_step(
        create_step()
    )

    plan.clear_steps()

    assert plan.steps == []
    assert plan.is_empty() is True


# ============================================================
# AgentPlan Ordering Tests
# ============================================================


def test_reorder_step():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    third = create_step(
        action="third"
    )

    plan.add_step(first)
    plan.add_step(second)
    plan.add_step(third)

    result = plan.reorder_step(
        third.id,
        0,
    )

    assert result is True

    assert [
        step.action
        for step in plan.steps
    ] == [
        "third",
        "first",
        "second",
    ]


def test_reorder_missing_step():

    plan = create_plan()

    result = plan.reorder_step(
        "missing",
        0,
    )

    assert result is False


def test_reorder_invalid_index():

    plan = create_plan()

    step = create_step()

    plan.add_step(
        step
    )

    with pytest.raises(
        AgentPlanError
    ):

        plan.reorder_step(
            step.id,
            5,
        )


# ============================================================
# AgentPlan Step Queries
# ============================================================


def test_pending_steps():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    plan.add_step(first)
    plan.add_step(second)

    first.start()
    first.complete()

    pending = plan.pending_steps()

    assert len(pending) == 1
    assert pending[0] is second


def test_completed_steps():

    plan = create_plan()

    first = create_step(
        action="first"
    )

    second = create_step(
        action="second"
    )

    plan.add_step(first)
    plan.add_step(second)

    first.start()
    first.complete()

    completed = plan.completed_steps()

    assert len(completed) == 1
    assert completed[0] is first


def test_failed_steps():

    plan = create_plan()

    first = create_step()

    plan.add_step(
        first
    )

    first.start()
    first.fail(
        "error"
    )

    failed = plan.failed_steps()

    assert len(failed) == 1
    assert failed[0] is first


def test_plan_is_empty():

    plan = create_plan()

    assert plan.is_empty() is True


def test_plan_is_complete():

    plan = create_plan()

    first = create_step()
    second = create_step()

    plan.add_step(first)
    plan.add_step(second)

    assert plan.is_complete() is False

    first.start()
    first.complete()

    second.start()
    second.complete()

    assert plan.is_complete() is True


# ============================================================
# AgentPlan Lifecycle Tests
# ============================================================


def test_prepare_plan():

    plan = create_plan()

    plan.add_step(
        create_step()
    )

    result = plan.prepare()

    assert result is True
    assert plan.status == "ready"
    assert plan.is_ready() is True


def test_prepare_empty_plan():

    plan = create_plan()

    with pytest.raises(
        AgentPlanError
    ):

        plan.prepare()


def test_start_plan():

    plan = create_plan()

    plan.add_step(
        create_step()
    )

    plan.prepare()

    result = plan.start()

    assert result is True
    assert plan.status == "running"
    assert plan.is_running() is True


def test_start_unready_plan():

    plan = create_plan()

    result = plan.start()

    assert result is False
    assert plan.status == "draft"


def test_complete_plan():

    plan = create_plan()

    step = create_step()

    plan.add_step(
        step
    )

    plan.prepare()
    plan.start()

    step.start()
    step.complete(
        "done"
    )

    result = plan.complete()

    assert result is True
    assert plan.status == "completed"
    assert plan.is_completed() is True


def test_complete_incomplete_plan():

    plan = create_plan()

    plan.add_step(
        create_step()
    )

    result = plan.complete()

    assert result is False
    assert plan.status == "draft"


def test_fail_plan():

    plan = create_plan()

    result = plan.fail()

    assert result is True
    assert plan.status == "failed"
    assert plan.is_failed() is True


def test_cancel_plan():

    plan = create_plan()

    result = plan.cancel()

    assert result is True
    assert plan.status == "cancelled"
    assert plan.is_cancelled() is True


def test_reset_plan():

    plan = create_plan()

    step = create_step()

    plan.add_step(
        step
    )

    step.start()
    step.complete(
        "done"
    )

    plan.status = "completed"

    result = plan.reset()

    assert result is True
    assert plan.status == "draft"
    assert step.status == "pending"
    assert step.result is None
    assert step.error is None


# ============================================================
# AgentPlan Serialization Tests
# ============================================================


def test_plan_to_dict():

    plan = create_plan()

    step = create_step(
        action="calculate",
        parameters={
            "value": 10,
        },
        tool_name="calculator",
    )

    plan.add_step(
        step
    )

    data = plan.to_dict()

    assert data["id"] == plan.id
    assert data["agent_id"] == plan.agent_id
    assert data["name"] == "Test Plan"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["action"] == "calculate"


def test_plan_from_dict():

    agent = create_agent()

    original = AgentPlan(
        agent=agent,
        name="Restoration Plan",
        description="Restore test.",
    )

    original.add_step(
        create_step(
            action="calculate",
            parameters={
                "value": 20,
            },
            tool_name="calculator",
        )
    )

    data = original.to_dict()

    restored = AgentPlan.from_dict(
        agent,
        data,
    )

    assert restored.id == original.id
    assert restored.agent_id == original.agent_id
    assert restored.name == original.name
    assert restored.description == original.description
    assert restored.status == original.status
    assert len(restored.steps) == 1
    assert restored.steps[0].action == "calculate"


def test_plan_from_dict_wrong_agent():

    first_agent = create_agent()

    second_agent = Agent(
        name="Other Agent",
        action="test",
    )

    plan = AgentPlan(
        agent=first_agent
    )

    data = plan.to_dict()

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlan.from_dict(
            second_agent,
            data,
        )


def test_plan_from_invalid_dict():

    agent = create_agent()

    with pytest.raises(
        AgentPlanError
    ):

        AgentPlan.from_dict(
            agent,
            "invalid",
        )


def test_plan_repr():

    plan = create_plan()

    representation = repr(
        plan
    )

    assert "AgentPlan" in representation
    assert plan.id in representation


def test_plan_len():

    plan = create_plan()

    plan.add_step(
        create_step()
    )

    plan.add_step(
        create_step(
            action="second"
        )
    )

    assert len(plan) == 2


# ============================================================
# AgentPlanner Creation Tests
# ============================================================


def test_agent_planner_creation():

    planner = AgentPlanner()

    assert planner is not None


def test_agent_planner_repr():

    planner = AgentPlanner()

    representation = repr(
        planner
    )

    assert "AgentPlanner" in representation


# ============================================================
# AgentPlanner Plan Creation Tests
# ============================================================


def test_create_plan():

    planner = AgentPlanner()
    agent = create_agent()

    plan = planner.create_plan(
        agent,
        name="My Plan",
        description="My description",
    )

    assert isinstance(
        plan,
        AgentPlan,
    )

    assert plan.agent_id == agent.id
    assert plan.name == "My Plan"
    assert plan.description == "My description"


def test_create_plan_invalid_agent():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.create_plan(
            "invalid"
        )


# ============================================================
# AgentPlanner Step Creation Tests
# ============================================================


def test_create_step():

    planner = AgentPlanner()

    step = planner.create_step(
        action="calculate",
        description="Calculate value",
        parameters={
            "value": 10,
        },
        tool_name="calculator",
    )

    assert isinstance(
        step,
        AgentPlanStep,
    )

    assert step.action == "calculate"
    assert step.description == "Calculate value"
    assert step.parameters == {
        "value": 10,
    }
    assert step.tool_name == "calculator"


def test_create_step_invalid_action():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.create_step(
            action=""
        )


# ============================================================
# AgentPlanner Add Step Tests
# ============================================================


def test_planner_add_step():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )
    step = planner.create_step(
        action="test"
    )

    result = planner.add_step(
        plan,
        step,
    )

    assert result is True
    assert len(plan.steps) == 1


def test_planner_add_step_invalid_plan():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.add_step(
            "invalid",
            create_step(),
        )


# ============================================================
# AgentPlanner Validation Tests
# ============================================================


def test_validate_plan():

    planner = AgentPlanner()
    agent = create_agent()

    plan = planner.create_plan(
        agent
    )

    plan.add_step(
        create_step()
    )

    result = planner.validate_plan(
        plan,
        agent,
    )

    assert result is True


def test_validate_plan_wrong_agent():

    planner = AgentPlanner()

    first_agent = create_agent()

    second_agent = Agent(
        name="Other",
        action="test",
    )

    plan = planner.create_plan(
        first_agent
    )

    with pytest.raises(
        AgentPlanError
    ):

        planner.validate_plan(
            plan,
            second_agent,
        )


def test_validate_invalid_plan():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.validate_plan(
            "invalid"
        )


# ============================================================
# AgentPlanner Prepare Tests
# ============================================================


def test_prepare_plan():

    planner = AgentPlanner()
    agent = create_agent()

    plan = planner.create_plan(
        agent
    )

    planner.add_step(
        plan,
        planner.create_step(
            action="test"
        ),
    )

    result = planner.prepare_plan(
        plan
    )

    assert result is True
    assert plan.status == "ready"


# ============================================================
# AgentPlanner Next Step Tests
# ============================================================


def test_get_next_step():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    first = planner.create_step(
        action="first"
    )

    second = planner.create_step(
        action="second"
    )

    plan.add_step(first)
    plan.add_step(second)

    result = planner.get_next_step(
        plan
    )

    assert result is first


def test_get_next_step_skips_completed():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    first = planner.create_step(
        action="first"
    )

    second = planner.create_step(
        action="second"
    )

    plan.add_step(first)
    plan.add_step(second)

    first.start()
    first.complete(
        "done"
    )

    result = planner.get_next_step(
        plan
    )

    assert result is second


def test_get_next_step_none_when_finished():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    step = planner.create_step(
        action="test"
    )

    plan.add_step(
        step
    )

    step.start()
    step.complete(
        "done"
    )

    result = planner.get_next_step(
        plan
    )

    assert result is None


def test_get_next_step_invalid_plan():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.get_next_step(
            "invalid"
        )


# ============================================================
# AgentPlanner Progress Tests
# ============================================================


def test_get_progress():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    first = planner.create_step(
        action="first"
    )

    second = planner.create_step(
        action="second"
    )

    third = planner.create_step(
        action="third"
    )

    plan.add_step(first)
    plan.add_step(second)
    plan.add_step(third)

    first.start()
    first.complete(
        "done"
    )

    second.skip()

    progress = planner.get_progress(
        plan
    )

    assert progress["total_steps"] == 3
    assert progress["completed_steps"] == 1
    assert progress["pending_steps"] == 1
    assert progress["skipped_steps"] == 1
    assert progress["failed_steps"] == 0

    assert progress["progress_percent"] == pytest.approx(
        66.6666666667
    )


def test_get_progress_empty_plan():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    progress = planner.get_progress(
        plan
    )

    assert progress["total_steps"] == 0
    assert progress["completed_steps"] == 0
    assert progress["progress_percent"] == 0.0


def test_get_progress_invalid_plan():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.get_progress(
            "invalid"
        )


# ============================================================
# AgentPlanner Reset Tests
# ============================================================


def test_reset_plan():

    planner = AgentPlanner()
    plan = planner.create_plan(
        create_agent()
    )

    step = planner.create_step(
        action="test"
    )

    plan.add_step(
        step
    )

    step.start()
    step.complete(
        "done"
    )

    plan.status = "completed"

    result = planner.reset_plan(
        plan
    )

    assert result is True
    assert plan.status == "draft"
    assert step.status == "pending"


def test_reset_invalid_plan():

    planner = AgentPlanner()

    with pytest.raises(
        AgentPlanError
    ):

        planner.reset_plan(
            "invalid"
        )