import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.agent_orchestrator import AgentOrchestrator
from modules.agent.agent_planner import AgentPlanner
from modules.agent.agent_runtime_context import (
    AgentRuntimeContext,
    AgentRuntimeContextError,
)
from modules.agent.tool import AgentTool
from modules.multimodal.voice_command_executor import VoiceCommandExecutor


def create_agent():
    def test_handler(**kwargs):
        return "Voice command executed successfully."

    tool = AgentTool(
        name="test_tool",
        description="Test tool for voice commands",
        enabled=True,
        handler=test_handler,
    )

    agent = Agent(
        name="Test Agent",
        description="Agent used for voice command executor tests",
    )

    agent.assign_tool(tool)

    engine = AgentEngine()
    engine.register_tool(tool)

    return agent, engine


def create_executor():
    agent, engine = create_agent()

    planner = AgentPlanner()

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
    )

    context = AgentRuntimeContext(
        agent=agent,
        query="test_tool",
    )

    executor = VoiceCommandExecutor(
        runtime_context=context,
        planner=planner,
        orchestrator=orchestrator,
    )

    return executor, context, orchestrator


def test_voice_command_executor_success():
    executor, context, orchestrator = create_executor()

    result = executor.execute()

    assert result["success"] is True
    assert result["query"] == "test_tool"

    assert result["plan_id"] is not None
    assert result["execution_id"] == str(result["plan_id"])

    assert result["result"] == [
        "Voice command executed successfully."
    ]

    assert context.plan is not None
    assert context.plan.status == "completed"

    execution_context = orchestrator.get_execution_context()

    assert execution_context is not None
    assert execution_context.execution_id == str(context.plan.id)

    assert orchestrator.is_completed() is True


def test_voice_command_executor_rejects_empty_query():
    executor, context, orchestrator = create_executor()

    context.set_query("   ")

    result = executor.execute()

    assert result["success"] is False
    assert result["error"] is not None
    assert "query" in result["error"].lower()

    assert context.plan is None
    assert orchestrator.get_execution_context() is None


def test_runtime_context_rejects_non_string_query():
    agent, _ = create_agent()

    context = AgentRuntimeContext(
        agent=agent,
        query="test_tool",
    )

    with pytest.raises(
        AgentRuntimeContextError,
        match="Query must be a string",
    ):
        context.set_query(None)


def test_voice_command_executor_rejects_unknown_command():
    executor, context, orchestrator = create_executor()

    context.set_query("unknown_voice_command")

    result = executor.execute()

    assert result["success"] is False
    assert result["error"] is not None

    assert context.plan is None

    # No plan means orchestration must never have started.
    assert orchestrator.get_execution_context() is None
    assert orchestrator.is_active() is False


def test_runtime_context_rejects_missing_agent():
    with pytest.raises(
        AgentRuntimeContextError,
        match="valid Agent",
    ):
        AgentRuntimeContext(
            agent=None,
            query="test_tool",
        )


def test_voice_command_executor_creates_single_step_plan():
    executor, context, orchestrator = create_executor()

    result = executor.execute()

    assert result["success"] is True
    assert context.plan is not None

    assert len(context.plan.steps) == 1

    step = context.plan.steps[0]

    assert step.tool_name == "test_tool"
    assert step.action == "test_tool"
    assert step.status == "completed"


def test_voice_command_executor_syncs_context_status():
    executor, context, orchestrator = create_executor()

    result = executor.execute()

    assert result["success"] is True

    assert context.status == "completed"
    assert context.plan is not None
    assert context.plan.status == "completed"

    assert orchestrator.is_completed() is True


def test_voice_command_executor_returns_progress():
    executor, context, orchestrator = create_executor()

    result = executor.execute()

    assert result["success"] is True

    progress = result["progress"]

    assert progress is not None
    assert progress["plan_id"] == context.plan.id
    assert progress["total_steps"] == 1
    assert progress["completed_steps"] == 1
    assert progress["failed_steps"] == 0
    assert progress["pending_steps"] == 0
    assert progress["skipped_steps"] == 0
    assert progress["progress_percent"] == 100.0


def test_voice_command_executor_does_not_execute_unknown_tool():
    executor, context, orchestrator = create_executor()

    context.set_query("missing_tool")

    result = executor.execute()

    assert result["success"] is False
    assert result["error"] is not None

    assert context.plan is None

    # Tool resolution failed before plan creation.
    assert orchestrator.get_execution_context() is None
    assert orchestrator.is_active() is False


def test_voice_command_executor_normalizes_query():
    executor, context, orchestrator = create_executor()

    context.set_query("   test_tool   ")

    result = executor.execute()

    assert result["success"] is True

    # AgentRuntimeContext owns query normalization.
    assert context.get_query() == "test_tool"
    assert result["query"] == "test_tool"

    assert context.plan is not None
    assert context.plan.steps[0].tool_name == "test_tool"