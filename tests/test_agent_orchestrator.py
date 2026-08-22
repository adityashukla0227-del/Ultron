"""
Ultron Agent Orchestrator Tests
Version: v0.41

Tests for:
- AgentOrchestrator initialization
- Plan validation
- Step resolution
- Single-step execution
- Sequential plan execution
- Successful tool execution
- Failed tool execution
- Plan completion
- Plan failure
- Safe execution
- Progress tracking
- Invalid inputs
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.agent_orchestrator import (
    AgentOrchestrator,
    AgentOrchestratorError,
)
from modules.agent.agent_planner import (
    AgentPlanError,
    AgentPlanner,
)
from modules.agent.tool import AgentTool
from modules.agent.tool_result import ToolResult


# ============================================================
# Helpers
# ============================================================


def create_agent(
    name: str = "Test Agent",
) -> Agent:
    """
    Create a valid test agent.
    """

    return Agent(
        name=name,
        description="Test agent",
        action="test_action",
    )


def create_engine() -> AgentEngine:
    """
    Create an engine with a simple runtime action.
    """

    engine = AgentEngine()

    engine.register_action(
        "test_action",
        lambda **parameters: parameters,
    )

    return engine


def create_tool(
    name: str = "test_tool",
    handler=None,
) -> AgentTool:
    """
    Create a test AgentTool.
    """

    if handler is None:
        handler = lambda **parameters: {
            "success": True,
            "parameters": parameters,
        }

    return AgentTool(
        name=name,
        description="Test tool",
        handler=handler,
    )


def create_tool_plan(
    agent: Agent,
    tool_name: str = "test_tool",
    parameters=None,
):
    """
    Create a prepared plan containing one tool step.
    """

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Test Plan",
        description="Test execution plan",
    )

    step = planner.create_step(
        action="execute_tool",
        description="Execute test tool",
        parameters=parameters or {},
        tool_name=tool_name,
    )

    planner.add_step(
        plan,
        step,
    )

    return planner, plan, step


# ============================================================
# Initialization
# ============================================================


def test_orchestrator_initialization():
    """
    Orchestrator should create default engine and planner.
    """

    orchestrator = AgentOrchestrator()

    assert isinstance(
        orchestrator.engine,
        AgentEngine,
    )

    assert isinstance(
        orchestrator.planner,
        AgentPlanner,
    )


def test_orchestrator_accepts_custom_engine_and_planner():
    """
    Orchestrator should preserve injected dependencies.
    """

    engine = create_engine()
    planner = AgentPlanner()

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    assert orchestrator.engine is engine
    assert orchestrator.planner is planner


# ============================================================
# Validation
# ============================================================


def test_validate_plan():
    """
    A valid plan belonging to the supplied agent should pass.
    """

    agent = create_agent()

    planner, plan, _ = create_tool_plan(
        agent
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    assert orchestrator.validate_plan(
        plan,
        agent,
    ) is True


def test_validate_plan_rejects_invalid_agent():
    """
    Non-Agent objects should be rejected.
    """

    orchestrator = AgentOrchestrator()

    with pytest.raises(
        AgentOrchestratorError
    ):
        orchestrator.validate_plan(
            object(),
            object(),
        )


def test_validate_plan_rejects_empty_plan():
    """
    Empty plans cannot be orchestrated.
    """

    agent = create_agent()

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Empty Plan",
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    with pytest.raises(
        AgentOrchestratorError
    ):
        orchestrator.validate_plan(
            plan,
            agent,
        )


def test_validate_plan_rejects_plan_for_different_agent():
    """
    A plan cannot be executed by another agent.
    """

    agent_one = create_agent(
        "Agent One"
    )

    agent_two = create_agent(
        "Agent Two"
    )

    planner, plan, _ = create_tool_plan(
        agent_one
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    with pytest.raises(
        AgentOrchestratorError
    ):
        orchestrator.validate_plan(
            plan,
            agent_two,
        )


# ============================================================
# Step Resolution
# ============================================================


def test_get_next_step_returns_pending_step():
    """
    The first pending step should be returned.
    """

    agent = create_agent()

    planner, plan, step = create_tool_plan(
        agent
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    result = orchestrator.get_next_step(
        plan
    )

    assert result is step


def test_get_next_step_returns_none_when_no_pending_steps():
    """
    No pending step should return None.
    """

    agent = create_agent()

    planner, plan, step = create_tool_plan(
        agent
    )

    step.complete(
        "done"
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    assert orchestrator.get_next_step(
        plan
    ) is None


# ============================================================
# Single Step Execution
# ============================================================


def test_execute_step_success():
    """
    A successful tool execution should complete the step.
    """

    agent = create_agent()

    engine = create_engine()

    tool = create_tool()

    engine.register_tool(
        tool
    )

    agent.assign_tool(
        tool
    )

    planner, plan, step = create_tool_plan(
        agent,
        parameters={
            "value": 42,
        },
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    result = orchestrator.execute_step(
        agent,
        step,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert step.is_completed()
    assert step.result is not None
    assert step.error is None


def test_execute_step_failure():
    """
    A failed tool execution should fail the step.
    """

    agent = create_agent()

    engine = create_engine()

    def failing_tool(**parameters):
        raise RuntimeError(
            "tool failure"
        )

    tool = create_tool(
        handler=failing_tool
    )

    engine.register_tool(
        tool
    )

    agent.assign_tool(
        tool
    )

    planner, plan, step = create_tool_plan(
        agent
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    result = orchestrator.execute_step(
        agent,
        step,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert step.is_failed()
    assert step.error is not None


def test_execute_step_rejects_step_without_tool():
    """
    A tool-backed orchestrator step requires a tool name.
    """

    agent = create_agent()

    planner = AgentPlanner()

    step = planner.create_step(
        action="execute_tool",
        description="Missing tool",
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    with pytest.raises(
        AgentOrchestratorError
    ):
        orchestrator.execute_step(
            agent,
            step,
        )


# ============================================================
# Sequential Plan Execution
# ============================================================


def test_execute_plan_success():
    """
    All successful steps should complete the plan.
    """

    agent = create_agent()

    engine = create_engine()

    execution_log = []

    def logging_tool(**parameters):
        execution_log.append(
            parameters["step"]
        )

        return {
            "step": parameters["step"],
        }

    tool = create_tool(
        handler=logging_tool
    )

    engine.register_tool(
        tool
    )

    agent.assign_tool(
        tool
    )

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Sequential Plan",
    )

    step_one = planner.create_step(
        action="execute_tool",
        description="First step",
        parameters={
            "step": 1,
        },
        tool_name="test_tool",
    )

    step_two = planner.create_step(
        action="execute_tool",
        description="Second step",
        parameters={
            "step": 2,
        },
        tool_name="test_tool",
    )

    planner.add_step(
        plan,
        step_one,
    )

    planner.add_step(
        plan,
        step_two,
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True
    assert plan.is_completed()

    assert step_one.is_completed()
    assert step_two.is_completed()

    assert execution_log == [
        1,
        2,
    ]


def test_execute_plan_stops_on_failed_step():
    """
    Plan execution should stop when a step fails.
    """

    agent = create_agent()

    engine = create_engine()

    execution_log = []

    def conditional_tool(**parameters):
        step_number = parameters["step"]

        execution_log.append(
            step_number
        )

        if step_number == 2:
            raise RuntimeError(
                "second step failed"
            )

        return step_number

    tool = create_tool(
        handler=conditional_tool
    )

    engine.register_tool(
        tool
    )

    agent.assign_tool(
        tool
    )

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Failure Plan",
    )

    step_one = planner.create_step(
        action="execute_tool",
        parameters={
            "step": 1,
        },
        tool_name="test_tool",
    )

    step_two = planner.create_step(
        action="execute_tool",
        parameters={
            "step": 2,
        },
        tool_name="test_tool",
    )

    step_three = planner.create_step(
        action="execute_tool",
        parameters={
            "step": 3,
        },
        tool_name="test_tool",
    )

    planner.add_step(
        plan,
        step_one,
    )

    planner.add_step(
        plan,
        step_two,
    )

    planner.add_step(
        plan,
        step_three,
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is False
    assert plan.is_failed()

    assert step_one.is_completed()
    assert step_two.is_failed()
    assert step_three.is_pending()

    assert execution_log == [
        1,
        2,
    ]


# ============================================================
# Safe Execution
# ============================================================


def test_execute_plan_safe_returns_failure_instead_of_raising():
    """
    Safe plan execution should return a structured failure.
    """

    agent = create_agent()

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Invalid Plan",
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    result = orchestrator.execute_plan_safe(
        agent,
        plan,
    )

    assert result["success"] is False
    assert result["plan_id"] == plan.id
    assert result["agent_id"] == agent.id
    assert result["error"] is not None


# ============================================================
# Progress
# ============================================================


def test_get_progress():
    """
    Orchestrator should expose planner progress.
    """

    agent = create_agent()

    planner, plan, step = create_tool_plan(
        agent
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    progress = orchestrator.get_progress(
        plan
    )

    assert progress["plan_id"] == plan.id
    assert progress["agent_id"] == agent.id
    assert progress["total_steps"] == 1
    assert progress["pending_steps"] == 1
    assert progress["completed_steps"] == 0
    assert progress["failed_steps"] == 0
    assert progress["progress_percent"] == 0.0


def test_get_progress_after_completed_step():
    """
    Completed steps should update progress.
    """

    agent = create_agent()

    planner, plan, step = create_tool_plan(
        agent
    )

    step.complete(
        "completed"
    )

    orchestrator = AgentOrchestrator(
        engine=create_engine(),
        planner=planner,
    )

    progress = orchestrator.get_progress(
        plan
    )

    assert progress["completed_steps"] == 1
    assert progress["pending_steps"] == 0
    assert progress["progress_percent"] == 100.0


# ============================================================
# Representation
# ============================================================


def test_orchestrator_repr():
    """
    Orchestrator should provide a useful representation.
    """

    orchestrator = AgentOrchestrator()

    representation = repr(
        orchestrator
    )

    assert "AgentOrchestrator" in representation