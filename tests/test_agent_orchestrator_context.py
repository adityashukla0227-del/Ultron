"""
Tests for Ultron Agent Orchestrator Execution Context Integration
Version: v0.50

Tests for:
- Automatic ExecutionContext creation
- Context identity
- Context lifecycle synchronization
- Total step synchronization
- Current step tracking
- Completed step tracking
- Failed step tracking
- Retry tracking
- Skip tracking
- Retry count synchronization
- Skip count synchronization
- Successful plan completion
- Failed plan execution
- Cancellation synchronization
- Pause / resume synchronization
- Context snapshots
- Context reset
- Context query integration
- Terminal state consistency
- Context/controller synchronization
- Result/state consistency
- Snapshot completeness
- Defensive edge cases
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_engine import AgentEngine
from modules.agent.agent_orchestrator import (
    AgentOrchestrator,
    AgentOrchestratorError,
)
from modules.agent.agent_planner import AgentPlanner
from modules.agent.agent_execution_controller import (
    AgentExecutionController,
)
from modules.agent.execution_context import ExecutionContext
from modules.agent.execution_event_emitter import (
    ExecutionEventEmitter,
)
from modules.agent.tool import AgentTool


# ============================================================
# Helpers
# ============================================================


def create_agent(
    name: str = "Context Test Agent",
) -> Agent:
    """Create a valid test agent."""

    return Agent(
        name=name,
        description="Execution context test agent",
        action="test_action",
    )


def create_engine() -> AgentEngine:
    """Create an engine with a simple runtime action."""

    engine = AgentEngine()

    engine.register_action(
        "test_action",
        lambda **parameters: parameters,
    )

    return engine


def create_tool(
    name: str = "context_tool",
    handler=None,
) -> AgentTool:
    """Create a test tool."""

    if handler is None:
        handler = lambda **parameters: {
            "success": True,
            "parameters": parameters,
        }

    return AgentTool(
        name=name,
        description="Context integration test tool",
        handler=handler,
    )


def create_orchestrator(
    agent: Agent,
    tool: AgentTool,
) -> tuple[
    AgentOrchestrator,
    AgentPlanner,
]:
    """Create an orchestrator with a registered test tool."""

    engine = create_engine()

    engine.register_tool(
        tool
    )

    agent.assign_tool(
        tool
    )

    planner = AgentPlanner()

    orchestrator = AgentOrchestrator(
        engine=engine,
        planner=planner,
        controller=AgentExecutionController(),
        emitter=ExecutionEventEmitter(),
    )

    return orchestrator, planner


def create_plan(
    planner: AgentPlanner,
    agent: Agent,
    step_count: int = 1,
):
    """Create a plan containing tool steps."""

    plan = planner.create_plan(
        agent=agent,
        name="Context Integration Plan",
        description="Execution context integration test plan",
    )

    for index in range(step_count):
        step = planner.create_step(
            action="execute_tool",
            description=f"Context step {index + 1}",
            parameters={
                "step": index + 1,
            },
            tool_name="context_tool",
        )

        planner.add_step(
            plan,
            step,
        )

    return plan


# ============================================================
# Context Creation
# ============================================================


def test_execution_context_is_created_automatically():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    assert orchestrator.get_execution_context() is None

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert isinstance(
        context,
        ExecutionContext,
    )


def test_execution_context_identity_matches_execution():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.execution_id == str(
        plan.id
    )

    assert context.plan_id == str(
        plan.id
    )

    assert context.agent_id == str(
        agent.id
    )

    assert result["plan_id"] == plan.id
    assert result["agent_id"] == agent.id


# ============================================================
# Total Steps
# ============================================================


def test_context_total_steps_matches_plan():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=3,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None
    assert context.total_steps == 3


# ============================================================
# Successful Execution
# ============================================================


def test_successful_execution_completes_context():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.is_completed()
    assert context.status == "completed"

    assert context.completed_steps == 2
    assert context.failed_steps == 0
    assert context.skipped_steps == 0
    assert context.retried_steps == 0

    assert context.current_step_id is None
    assert context.current_step_index is None

    assert context.started_at is not None
    assert context.completed_at is not None


def test_successful_steps_store_results_in_context():

    agent = create_agent()

    def handler(**parameters):
        return {
            "value": parameters["step"],
        }

    tool = create_tool(
        handler=handler
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    results = context.get_results()

    assert len(results) == 2

    for step in plan.steps:
        assert step.id in results


# ============================================================
# Failed Execution
# ============================================================


def test_failed_execution_fails_context():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "context test failure"
        )

    tool = create_tool(
        handler=failing_handler
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is False

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.is_failed()
    assert context.status == "failed"

    assert context.failed_steps == 1

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_failed_step_error_is_stored_in_context():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "expected failure"
        )

    tool = create_tool(
        handler=failing_handler
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    step = plan.steps[0]

    stored = context.get_result(
        step.id
    )

    assert stored is not None
    assert stored["error"] == "expected failure"


# ============================================================
# Current Step Tracking
# ============================================================


def test_context_clears_current_step_after_success():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_context_clears_current_step_after_failure():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "failure"
        )

    tool = create_tool(
        handler=failing_handler
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.current_step_id is None
    assert context.current_step_index is None


# ============================================================
# Retry / Skip
# ============================================================


def test_retry_updates_context_counter():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    orchestrator.controller.start(
        plan,
        agent,
    )

    step = plan.steps[0]

    step.start()

    step.fail(
        "temporary failure"
    )

    result = orchestrator.retry_step(
        step
    )

    assert result is True

    context = orchestrator.get_execution_context()

    assert context is not None
    assert context.retried_steps == 1


def test_retry_updates_context_counter_for_multiple_retries():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    orchestrator.controller.start(
        plan,
        agent,
    )

    step = plan.steps[0]

    for expected_count in range(1, 4):

        step.start()

        step.fail(
            f"temporary failure {expected_count}"
        )

        result = orchestrator.retry_step(
            step
        )

        assert result is True

        context = orchestrator.get_execution_context()

        assert context is not None
        assert context.retried_steps == expected_count


def test_retry_context_snapshot_contains_retry_count():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    orchestrator.controller.start(
        plan,
        agent,
    )

    step = plan.steps[0]

    step.start()

    step.fail(
        "temporary failure"
    )

    assert orchestrator.retry_step(
        step
    ) is True

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None
    assert snapshot["retried_steps"] == 1


def test_skip_updates_context_counter():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    orchestrator.controller.start(
        plan,
        agent,
    )

    step = plan.steps[0]

    result = orchestrator.skip_step(
        step
    )

    assert result is True

    context = orchestrator.get_execution_context()

    assert context is not None
    assert context.skipped_steps == 1


def test_skip_context_snapshot_contains_skip_count():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    orchestrator.controller.start(
        plan,
        agent,
    )

    step = plan.steps[0]

    assert orchestrator.skip_step(
        step
    ) is True

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None
    assert snapshot["skipped_steps"] == 1


# ============================================================
# Snapshot
# ============================================================


def test_context_snapshot_after_successful_execution():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None

    assert snapshot["execution_id"] == str(
        plan.id
    )

    assert snapshot["plan_id"] == str(
        plan.id
    )

    assert snapshot["agent_id"] == str(
        agent.id
    )

    assert snapshot["status"] == "completed"

    assert snapshot["total_steps"] == 2
    assert snapshot["completed_steps"] == 2
    assert snapshot["failed_steps"] == 0
    assert snapshot["retried_steps"] == 0
    assert snapshot["skipped_steps"] == 0


def test_context_snapshot_is_defensive():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None

    snapshot["metadata"]["mutated"] = True

    fresh_snapshot = orchestrator.get_context_snapshot()

    assert fresh_snapshot is not None

    assert "mutated" not in fresh_snapshot["metadata"]


# ============================================================
# Reset
# ============================================================


def test_reset_execution_clears_context():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    assert orchestrator.get_execution_context() is not None

    orchestrator.reset_execution()

    assert orchestrator.get_execution_context() is None


# ============================================================
# Empty Context Snapshot
# ============================================================


def test_context_snapshot_is_none_before_execution():

    orchestrator = AgentOrchestrator()

    assert orchestrator.get_execution_context() is None
    assert orchestrator.get_context_snapshot() is None


# ============================================================
# Step 4 - Context Query Integration
# ============================================================


def test_context_queries_reflect_successful_execution():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=3,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.has_completed_steps()
    assert not context.has_failed_steps()
    assert not context.has_skipped_steps()

    assert context.get_processed_steps() == 3
    assert context.get_remaining_steps() == 0

    assert context.is_finished()
    assert context.is_completed()


def test_context_queries_reflect_failed_execution():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "query failure"
        )

    tool = create_tool(
        handler=failing_handler,
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is False

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.has_failed_steps()
    assert not context.has_completed_steps()

    assert context.get_processed_steps() == 1
    assert context.get_remaining_steps() == 1

    assert context.is_finished()
    assert context.is_failed()


def test_context_last_result_matches_last_completed_step():

    agent = create_agent()

    def handler(**parameters):
        return {
            "step": parameters["step"],
        }

    tool = create_tool(
        handler=handler,
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=3,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    last_result = context.get_last_result()

    assert last_result == {
        "step": 3,
    }


# ============================================================
# Step 4 - Terminal State Consistency
# ============================================================


def test_completed_context_is_terminal():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.status == "completed"
    assert context.is_finished()
    assert context.is_completed()
    assert not context.is_running()
    assert not context.is_paused()
    assert not context.is_failed()
    assert not context.is_cancelled()


def test_failed_context_is_terminal():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "terminal failure"
        )

    tool = create_tool(
        handler=failing_handler,
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is False

    context = orchestrator.get_execution_context()

    assert context is not None

    assert context.status == "failed"
    assert context.is_finished()
    assert context.is_failed()
    assert not context.is_running()
    assert not context.is_paused()
    assert not context.is_completed()
    assert not context.is_cancelled()


# ============================================================
# Step 4 - Result / State Consistency
# ============================================================


def test_successful_context_processed_steps_match_results():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
        )

    plan = create_plan(
        planner,
        agent,
        step_count=4,
    )

    result = orchestrator.execute_plan(
        agent,
        plan,
    )

    assert result["success"] is True

    context = orchestrator.get_execution_context()

    assert context is not None

    results = context.get_results()

    assert len(results) == context.completed_steps
    assert context.get_processed_steps() == 4
    assert context.get_remaining_steps() == 0


def test_failed_context_contains_failed_step_result():

    agent = create_agent()

    def failing_handler(**parameters):
        raise RuntimeError(
            "state consistency failure"
        )

    tool = create_tool(
        handler=failing_handler,
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    failed_step = plan.steps[0]

    assert context.has_result(
        failed_step.id
    )

    assert context.get_result(
        failed_step.id
    ) == {
        "error": "state consistency failure",
    }

    assert context.failed_steps == 1
    assert context.get_processed_steps() == 1
    assert context.get_remaining_steps() == 1


# ============================================================
# Step 4 - Snapshot Completeness
# ============================================================


def test_context_snapshot_contains_query_state():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=2,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None

    assert snapshot["status"] == "completed"
    assert snapshot["total_steps"] == 2
    assert snapshot["completed_steps"] == 2

    assert "progress" in snapshot

    assert snapshot["progress"]["processed_steps"] == 2
    assert snapshot["progress"]["percentage"] == 100.0


def test_context_snapshot_preserves_nested_result_defensiveness():

    agent = create_agent()

    def handler(**parameters):
        return {
            "nested": {
                "step": parameters["step"],
            },
        }

    tool = create_tool(
        handler=handler,
    )

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=1,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    snapshot = orchestrator.get_context_snapshot()

    assert snapshot is not None

    step_id = plan.steps[0].id

    snapshot["results"][step_id]["nested"]["step"] = 999

    fresh_snapshot = orchestrator.get_context_snapshot()

    assert fresh_snapshot is not None

    assert (
        fresh_snapshot["results"][step_id]["nested"]["step"]
        == 1
    )


# ============================================================
# Step 4 - Defensive Edge Cases
# ============================================================


def test_context_snapshot_returns_none_after_reset():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
    )

    orchestrator.execute_plan(
        agent,
        plan,
    )

    assert orchestrator.get_context_snapshot() is not None

    orchestrator.reset_execution()

    assert orchestrator.get_context_snapshot() is None


def test_new_plan_gets_new_execution_context():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    first_plan = create_plan(
        planner,
        agent,
        step_count=1,
    )

    orchestrator.execute_plan(
        agent,
        first_plan,
    )

    first_context = orchestrator.get_execution_context()

    assert first_context is not None

    orchestrator.reset_execution()

    second_plan = create_plan(
        planner,
        agent,
        step_count=1,
    )

    orchestrator.execute_plan(
        agent,
        second_plan,
    )

    second_context = orchestrator.get_execution_context()

    assert second_context is not None

    assert (
        first_context.execution_id
        != second_context.execution_id
    )

    assert (
        second_context.execution_id
        == str(second_plan.id)
    )


def test_context_remaining_steps_never_becomes_negative():

    agent = create_agent()
    tool = create_tool()

    orchestrator, planner = create_orchestrator(
        agent,
        tool,
    )

    plan = create_plan(
        planner,
        agent,
        step_count=1,
    )

    orchestrator._context_start(
        plan,
        agent,
    )

    context = orchestrator.get_execution_context()

    assert context is not None

    context.record_completed_step(
        plan.steps[0].id,
        "done",
    )

    context.record_completed_step(
        "extra-step",
        "done",
    )

    assert context.get_remaining_steps() == 0
    assert context.get_remaining_steps() >= 0


def test_context_query_methods_are_safe_before_execution():

    orchestrator = AgentOrchestrator()

    assert orchestrator.get_execution_context() is None

    assert orchestrator.get_context_snapshot() is None
