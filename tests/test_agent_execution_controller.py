"""
Tests for Ultron Agent Execution Controller
Version: v0.44
"""

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_planner import (
    AgentPlan,
    AgentPlanStep,
)
from modules.agent.agent_execution_controller import (
    AgentExecutionController,
    AgentExecutionControllerError,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def agent():
    return Agent(
        name="Test Agent",
        description="Execution controller test agent",
    )


@pytest.fixture
def plan(agent):
    return AgentPlan(
        agent=agent,
        name="Test Plan",
        description="Execution controller test plan",
    )


@pytest.fixture
def step():
    return AgentPlanStep(
        action="test_action",
        description="Test execution step",
        tool_name="test_tool",
    )


@pytest.fixture
def controller():
    return AgentExecutionController()


# ============================================================
# Initialization
# ============================================================


def test_controller_initial_state():
    controller = AgentExecutionController()

    assert controller.state == "idle"
    assert controller.current_plan_id is None
    assert controller.current_agent_id is None
    assert controller.current_step_id is None
    assert controller.max_retries == 3
    assert controller.retry_counts == {}
    assert controller.execution_history == []


def test_controller_custom_retry_limit():
    controller = AgentExecutionController(
        max_retries=5
    )

    assert controller.max_retries == 5


def test_controller_rejects_invalid_retry_limit():
    with pytest.raises(
        AgentExecutionControllerError
    ):
        AgentExecutionController(
            max_retries="3"
        )


def test_controller_rejects_negative_retry_limit():
    with pytest.raises(
        AgentExecutionControllerError
    ):
        AgentExecutionController(
            max_retries=-1
        )


# ============================================================
# Validation
# ============================================================


def test_validate_plan(controller, plan, agent):
    assert controller.validate_plan(
        plan,
        agent,
    ) is True


def test_validate_plan_rejects_invalid_plan(
    controller,
    agent,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.validate_plan(
            "invalid",
            agent,
        )


def test_validate_plan_rejects_invalid_agent(
    controller,
    plan,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.validate_plan(
            plan,
            "invalid",
        )


def test_validate_plan_rejects_wrong_agent(
    controller,
    plan,
):
    other_agent = Agent(
        name="Other Agent",
        description="Different agent",
    )

    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.validate_plan(
            plan,
            other_agent,
        )


# ============================================================
# Start
# ============================================================


def test_start_execution(
    controller,
    plan,
    agent,
):
    assert controller.start(
        plan,
        agent,
    ) is True

    assert controller.state == "running"
    assert controller.current_plan_id == plan.id
    assert controller.current_agent_id == agent.id
    assert controller.current_step_id is None


def test_start_records_event(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    history = controller.get_history()

    assert len(history) == 1
    assert history[0]["event"] == "execution_started"
    assert history[0]["plan_id"] == plan.id
    assert history[0]["agent_id"] == agent.id


def test_start_clears_previous_execution_data(
    controller,
    plan,
    agent,
):
    controller.retry_counts["old-step"] = 2
    controller.execution_history.append(
        {
            "event": "old_event"
        }
    )

    controller.start(
        plan,
        agent,
    )

    assert controller.retry_counts == {}

    history = controller.get_history()

    assert len(history) == 1
    assert history[0]["event"] == "execution_started"


def test_start_rejects_active_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.start(
            plan,
            agent,
        )


def test_start_rejects_cancelled_plan(
    controller,
    plan,
    agent,
):
    plan.cancel()

    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.start(
            plan,
            agent,
        )


# ============================================================
# Pause / Resume
# ============================================================


def test_pause_running_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.pause() is True
    assert controller.state == "paused"
    assert controller.is_paused() is True
    assert controller.is_active() is True


def test_pause_non_running_execution(
    controller,
):
    assert controller.pause() is False
    assert controller.state == "idle"


def test_resume_paused_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.pause()

    assert controller.resume() is True
    assert controller.state == "running"
    assert controller.is_running() is True


def test_resume_non_paused_execution(
    controller,
):
    assert controller.resume() is False


def test_pause_resume_events(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.pause()
    controller.resume()

    events = [
        item["event"]
        for item in controller.get_history()
    ]

    assert events == [
        "execution_started",
        "execution_paused",
        "execution_resumed",
    ]


# ============================================================
# Cancel
# ============================================================


def test_cancel_running_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.cancel() is True

    assert controller.state == "cancelled"
    assert controller.is_cancelled() is True
    assert controller.is_active() is False


def test_cancel_paused_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.pause()

    assert controller.cancel() is True
    assert controller.state == "cancelled"


def test_cancel_idle_execution(
    controller,
):
    assert controller.cancel() is False


def test_cancel_records_event(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.cancel()

    assert (
        controller.get_history()[-1]["event"]
        == "execution_cancelled"
    )


# ============================================================
# Complete / Fail
# ============================================================


def test_complete_running_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.complete() is True
    assert controller.state == "completed"
    assert controller.is_completed() is True
    assert controller.current_step_id is None


def test_complete_non_running_execution(
    controller,
):
    assert controller.complete() is False


def test_fail_running_execution(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.fail(
        "Something failed."
    ) is True

    assert controller.state == "failed"
    assert controller.is_failed() is True


def test_fail_records_error(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.fail(
        "Tool execution failed."
    )

    event = controller.get_history()[-1]

    assert event["event"] == "execution_failed"
    assert event["error"] == "Tool execution failed."


def test_fail_idle_execution(
    controller,
):
    assert controller.fail(
        "failure"
    ) is False


# ============================================================
# Current Step
# ============================================================


def test_set_current_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.set_current_step(
        step
    ) is True

    assert controller.current_step_id == step.id


def test_set_current_step_rejects_invalid_step(
    controller,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.set_current_step(
            "invalid"
        )


def test_set_current_step_requires_running_state(
    controller,
    step,
):
    assert controller.set_current_step(
        step
    ) is False


def test_set_current_step_records_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.set_current_step(
        step
    )

    event = controller.get_history()[-1]

    assert event["event"] == "step_started"
    assert event["step_id"] == step.id


def test_clear_current_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.set_current_step(
        step
    )

    assert controller.clear_current_step() is True
    assert controller.current_step_id is None


# ============================================================
# Retry
# ============================================================


def test_failed_step_can_retry(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    step.fail(
        "Temporary failure."
    )

    assert controller.can_retry(
        step
    ) is True


def test_pending_step_cannot_retry(
    controller,
    step,
):
    assert controller.retry_step(
        step
    ) is False


def test_retry_failed_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    step.fail(
        "Temporary failure."
    )

    assert controller.retry_step(
        step
    ) is True

    assert step.is_pending() is True
    assert controller.get_retry_count(
        step
    ) == 1


def test_retry_increments_count(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    for expected in range(1, 4):

        step.fail(
            "Temporary failure."
        )

        assert controller.retry_step(
            step
        ) is True

        assert controller.get_retry_count(
            step
        ) == expected


def test_retry_limit_is_enforced(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    for _ in range(3):

        step.fail(
            "Temporary failure."
        )

        assert controller.retry_step(
            step
        ) is True

    step.fail(
        "Final failure."
    )

    assert controller.can_retry(
        step
    ) is False

    assert controller.retry_step(
        step
    ) is False


def test_retry_records_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    step.fail(
        "Temporary failure."
    )

    controller.retry_step(
        step
    )

    event = controller.get_history()[-1]

    assert event["event"] == "step_retry"
    assert event["step_id"] == step.id
    assert event["retry_count"] == 1


def test_retry_invalid_step(
    controller,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.retry_step(
            "invalid"
        )


def test_can_retry_invalid_step(
    controller,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.can_retry(
            "invalid"
        )


# ============================================================
# Skip
# ============================================================


def test_skip_pending_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.skip_step(
        step
    ) is True

    assert step.is_skipped() is True


def test_skip_non_pending_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    step.complete(
        "done"
    )

    assert controller.skip_step(
        step
    ) is False


def test_skip_records_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.skip_step(
        step
    )

    event = controller.get_history()[-1]

    assert event["event"] == "step_skipped"
    assert event["step_id"] == step.id


def test_skip_invalid_step(
    controller,
):
    with pytest.raises(
        AgentExecutionControllerError
    ):
        controller.skip_step(
            "invalid"
        )


# ============================================================
# State Queries
# ============================================================


def test_state_queries(
    controller,
    plan,
    agent,
):
    assert controller.is_running() is False
    assert controller.is_paused() is False
    assert controller.is_cancelled() is False
    assert controller.is_completed() is False
    assert controller.is_failed() is False
    assert controller.is_active() is False

    controller.start(
        plan,
        agent,
    )

    assert controller.is_running() is True
    assert controller.is_active() is True

    controller.pause()

    assert controller.is_paused() is True
    assert controller.is_active() is True

    controller.cancel()

    assert controller.is_cancelled() is True
    assert controller.is_active() is False


# ============================================================
# History
# ============================================================


def test_history_returns_copy(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    history = controller.get_history()

    history.clear()

    assert len(
        controller.get_history()
    ) == 1


# ============================================================
# Status
# ============================================================


def test_get_status(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    status = controller.get_status()

    assert status["state"] == "running"
    assert status["plan_id"] == plan.id
    assert status["agent_id"] == agent.id
    assert status["current_step_id"] is None
    assert status["max_retries"] == 3
    assert status["retry_counts"] == {}
    assert status["history_size"] == 1


def test_get_status_after_step(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.set_current_step(
        step
    )

    status = controller.get_status()

    assert status["current_step_id"] == step.id
    assert status["history_size"] == 2


# ============================================================
# Reset
# ============================================================


def test_reset_controller(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.set_current_step(
        step
    )

    step.fail(
        "Failure."
    )

    controller.retry_step(
        step
    )

    assert controller.reset() is True

    assert controller.state == "idle"
    assert controller.current_plan_id is None
    assert controller.current_agent_id is None
    assert controller.current_step_id is None
    assert controller.retry_counts == {}
    assert controller.execution_history == []


# ============================================================
# Representation
# ============================================================


def test_repr():
    controller = AgentExecutionController(
        max_retries=2
    )

    representation = repr(
        controller
    )

    assert "AgentExecutionController" in representation
    assert "state='idle'" in representation
    assert "max_retries=2" in representation


# ============================================================
# v0.44 — Structured Execution Observability
# ============================================================


def test_execution_id_created_on_start(
    controller,
    plan,
    agent,
):
    assert controller.get_execution_id() is None

    assert controller.start(
        plan,
        agent,
    ) is True

    execution_id = controller.get_execution_id()

    assert execution_id is not None
    assert isinstance(execution_id, str)
    assert execution_id.strip()


def test_execution_started_structured_event(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    events = controller.get_events()

    assert len(events) == 1

    event = events[0]

    assert event.event_type.value == "execution_started"
    assert event.execution_id == controller.get_execution_id()
    assert event.metadata["plan_id"] == plan.id
    assert event.metadata["agent_id"] == agent.id


def test_pause_resume_structured_events(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.pause() is True
    assert controller.resume() is True

    events = controller.get_events()

    assert [
        event.event_type.value
        for event in events
    ] == [
        "execution_started",
        "execution_paused",
        "execution_resumed",
    ]


def test_step_started_structured_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.set_current_step(
        step
    ) is True

    events = controller.get_step_events(
        step.id
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type.value == "step_started"
    assert event.execution_id == controller.get_execution_id()
    assert event.step_id == step.id


def test_retry_structured_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    controller.set_current_step(
        step
    )

    step.fail(
        "Failure."
    )

    assert controller.retry_step(
        step
    ) is True

    events = controller.get_step_events(
        step.id
    )

    assert [
        event.event_type.value
        for event in events
    ] == [
        "step_started",
        "step_retried",
    ]

    assert events[-1].metadata["retry_count"] == 1


def test_skip_structured_event(
    controller,
    plan,
    agent,
    step,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.skip_step(
        step
    ) is True

    events = controller.get_step_events(
        step.id
    )

    assert len(events) == 1

    assert events[0].event_type.value == "step_skipped"


def test_latest_event(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    controller.pause()

    latest = controller.get_latest_event()

    assert latest is not None
    assert latest.event_type.value == "execution_paused"


def test_event_count(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    assert controller.get_event_count() == 1

    controller.pause()

    assert controller.get_event_count() == 2

    controller.resume()

    assert controller.get_event_count() == 3


def test_status_contains_observability_data(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    status = controller.get_status()

    assert status["execution_id"] == controller.get_execution_id()
    assert status["event_count"] == 1


def test_reset_clears_structured_events(
    controller,
    plan,
    agent,
):
    controller.start(
        plan,
        agent,
    )

    execution_id = controller.get_execution_id()

    assert controller.get_event_count() == 1

    assert controller.reset() is True

    assert controller.get_execution_id() is None
    assert controller.get_events() == []
    assert controller.get_event_count() == 0

    assert controller.event_store.get_events(
        execution_id
    ) == []