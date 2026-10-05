"""
Ultron Execution Feedback Integration Tests.
Version: v0.84

Tests the integration boundary:

AgentOrchestrator
    ↓
ExecutionResult
    ↓
ExecutionFeedbackAdapter
    ↓
ExecutionFeedback
"""

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.agent_orchestrator import AgentOrchestrator
from modules.agent.agent_planner import AgentPlanner
from modules.agent.authorization import AuthorizationService
from modules.agent.execution_feedback import ExecutionFeedback
from modules.agent.execution_feedback_adapter import (
    ExecutionFeedbackAdapter,
)
from modules.agent.execution_result import ExecutionResult
from modules.agent.permission import Permission
from modules.agent.permission_registry import PermissionRegistry
from modules.agent.tool_permission_mapping import ToolPermissionMapping


def create_agent(
    name: str = "Integration Test Agent",
) -> Agent:
    """Create a valid test agent."""

    return Agent(
        name=name,
        description="Integration test agent",
        action="test_action",
    )


def create_engine() -> AgentEngine:
    """Create an engine with a simple runtime action."""

    permission_registry = PermissionRegistry(
        [
            Permission(
                name="test_tool_execute",
                description="Execute integration test tools.",
            )
        ]
    )

    tool_permission_mapping = ToolPermissionMapping(
        {
            "test_tool": [
                "test_tool_execute",
            ],
        }
    )

    engine = AgentEngine(
        authorization_service=AuthorizationService(
            permission_registry
        ),
        tool_permission_mapping=tool_permission_mapping,
    )

    engine.register_action(
        "test_action",
        lambda **parameters: parameters,
    )

    return engine


def create_tool(
    name: str = "test_tool",
) -> object:
    """Create a simple test tool."""

    from modules.agent.tool import AgentTool

    return AgentTool(
        name=name,
        description="Integration test tool",
        handler=lambda **parameters: parameters,
    )


def test_successful_execution_result_converts_to_feedback():
    """
    A successful orchestrator ExecutionResult should convert
    into completed consumer-facing ExecutionFeedback.
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

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Feedback Integration Plan",
    )

    step = planner.create_step(
        action="execute_tool",
        description="Execute integration test tool",
        parameters={
            "value": 42,
        },
        tool_name="test_tool",
    )

    planner.add_step(
        plan,
        step,
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    execution_result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert isinstance(
        execution_result,
        ExecutionResult,
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        execution_result
    )

    assert isinstance(
        feedback,
        ExecutionFeedback,
    )

    assert feedback.execution_id == (
        execution_result.execution_id
    )

    assert feedback.status == "completed"

    assert feedback.error is None

    assert feedback.metadata["plan_id"] == plan.id

    assert feedback.metadata["agent_id"] == agent.id

    assert isinstance(
        feedback.progress,
        dict,
    )


def test_failed_execution_result_converts_to_failed_feedback():
    """
    A failed orchestrator ExecutionResult should convert
    into failed consumer-facing ExecutionFeedback.
    """

    agent = create_agent()

    permission_registry = PermissionRegistry(
        [
            Permission(
                name="failing_tool_execute",
                description="Execute the failing integration test tool.",
            )
        ]
    )

    tool_permission_mapping = ToolPermissionMapping(
        {
            "failing_tool": [
                "failing_tool_execute",
            ],
        }
    )

    engine = AgentEngine(
        authorization_service=AuthorizationService(
            permission_registry
        ),
        tool_permission_mapping=tool_permission_mapping,
    )

    def failing_tool(**parameters):
        raise RuntimeError(
            "integration test failure"
        )

    from modules.agent.tool import AgentTool

    tool = AgentTool(
        name="failing_tool",
        description="Failing integration test tool",
        handler=failing_tool,
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
        name="Failed Feedback Integration Plan",
    )

    step = planner.create_step(
        action="execute_tool",
        description="Execute failing integration test tool",
        parameters={},
        tool_name="failing_tool",
    )

    planner.add_step(
        plan,
        step,
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    execution_result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert isinstance(
        execution_result,
        ExecutionResult,
    )

    assert execution_result.success is False

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        execution_result
    )

    assert isinstance(
        feedback,
        ExecutionFeedback,
    )

    assert feedback.execution_id == (
        execution_result.execution_id
    )

    assert feedback.status == "failed"

    assert feedback.error is not None

    assert feedback.metadata["plan_id"] == plan.id

    assert feedback.metadata["agent_id"] == agent.id


def test_adapter_preserves_execution_result_boundary():
    """
    Converting an ExecutionResult into feedback must not replace
    or mutate the canonical ExecutionResult boundary.
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

    planner = AgentPlanner()

    plan = planner.create_plan(
        agent=agent,
        name="Boundary Test Plan",
    )

    step = planner.create_step(
        action="execute_tool",
        description="Boundary test",
        parameters={
            "value": "boundary",
        },
        tool_name="test_tool",
    )

    planner.add_step(
        plan,
        step,
    )

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    execution_result = orchestrator.execute_plan(
        agent,
        plan,
    )

    original_result = execution_result.result
    original_metadata = execution_result.metadata
    original_execution_id = execution_result.execution_id

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        execution_result
    )

    assert isinstance(
        execution_result,
        ExecutionResult,
    )

    assert execution_result.execution_id == (
        original_execution_id
    )

    assert execution_result.result == original_result

    assert execution_result.metadata == original_metadata

    assert feedback.execution_id == original_execution_id
