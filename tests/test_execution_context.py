"""
Ultron Execution Context Tests
Version: v0.50

Tests for:
- ExecutionContext initialization
- Input validation
- Lifecycle management
- Pause / resume
- Cancellation
- Failure
- Completion
- Step tracking
- Step results
- Failure tracking
- Skip tracking
- Retry tracking
- Metadata
- Context queries
- Result queries
- Processed / remaining steps
- Progress tracking
- Snapshots
- Defensive copies
- Representation
"""

from datetime import datetime, timezone

import pytest

from modules.agent.execution_context import (
    ExecutionContext,
    ExecutionContextError,
)


# ============================================================
# Initialization
# ============================================================


def test_execution_context_initialization():
    """
    ExecutionContext should initialize with valid defaults.
    """

    context = ExecutionContext(
        "execution-1",
        plan_id="plan-1",
        agent_id="agent-1",
    )

    assert context.execution_id == "execution-1"
    assert context.plan_id == "plan-1"
    assert context.agent_id == "agent-1"

    assert context.status == "created"

    assert context.current_step_id is None
    assert context.current_step_index is None

    assert context.completed_steps == 0
    assert context.failed_steps == 0
    assert context.skipped_steps == 0
    assert context.retried_steps == 0
    assert context.total_steps == 0

    assert context.started_at is None
    assert context.completed_at is None

    assert context.metadata == {}
    assert context.get_results() == {}


def test_execution_context_accepts_metadata():

    context = ExecutionContext(
        "execution-1",
        metadata={
            "source": "test",
            "priority": "high",
        },
    )

    assert context.get_metadata("source") == "test"
    assert context.get_metadata("priority") == "high"


# ============================================================
# Validation
# ============================================================


def test_execution_context_rejects_empty_execution_id():

    with pytest.raises(ExecutionContextError):
        ExecutionContext("")


def test_execution_context_rejects_non_string_execution_id():

    with pytest.raises(ExecutionContextError):
        ExecutionContext(123)


def test_execution_context_rejects_invalid_plan_id():

    with pytest.raises(ExecutionContextError):
        ExecutionContext(
            "execution-1",
            plan_id=123,
        )


def test_execution_context_rejects_invalid_agent_id():

    with pytest.raises(ExecutionContextError):
        ExecutionContext(
            "execution-1",
            agent_id=123,
        )


# ============================================================
# Lifecycle
# ============================================================


def test_context_start():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    assert context.status == "running"
    assert context.is_running()
    assert context.started_at is not None
    assert isinstance(
        context.started_at,
        datetime,
    )

    assert context.started_at.tzinfo == timezone.utc


def test_context_start_preserves_original_started_at():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    started_at = context.started_at

    context.start()

    assert context.started_at == started_at


def test_context_cannot_start_after_completion():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.complete()

    with pytest.raises(ExecutionContextError):
        context.start()


def test_context_pause():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.pause()

    assert context.is_paused()
    assert context.status == "paused"


def test_context_pause_requires_running_state():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.pause()


def test_context_resume():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.pause()
    context.resume()

    assert context.is_running()
    assert context.status == "running"


def test_context_resume_requires_paused_state():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.resume()


def test_context_cancel():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    context.set_current_step(
        "step-1",
        step_index=0,
    )

    context.cancel()

    assert context.is_cancelled()
    assert context.status == "cancelled"

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_context_cannot_cancel_completed_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.complete()

    with pytest.raises(ExecutionContextError):
        context.cancel()


def test_context_fail():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    context.set_current_step(
        "step-1",
        step_index=0,
    )

    context.fail()

    assert context.is_failed()
    assert context.status == "failed"

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_context_cannot_fail_completed_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.complete()

    with pytest.raises(ExecutionContextError):
        context.fail()


def test_context_complete():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    context.set_current_step(
        "step-1",
        step_index=0,
    )

    context.complete()

    assert context.is_completed()
    assert context.status == "completed"

    assert context.completed_at is not None

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_context_cannot_complete_failed_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.fail()

    with pytest.raises(ExecutionContextError):
        context.complete()


def test_context_cannot_complete_cancelled_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.cancel()

    with pytest.raises(ExecutionContextError):
        context.complete()


# ============================================================
# Step Tracking
# ============================================================


def test_set_total_steps():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_total_steps(5)

    assert context.total_steps == 5


def test_set_total_steps_rejects_non_integer():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_total_steps("5")


def test_set_total_steps_rejects_negative_value():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_total_steps(-1)


def test_set_current_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_current_step(
        "step-1",
        step_index=2,
    )

    assert context.current_step_id == "step-1"
    assert context.current_step_index == 2


def test_set_current_step_without_index():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_current_step(
        "step-1"
    )

    assert context.current_step_id == "step-1"
    assert context.current_step_index is None


def test_set_current_step_rejects_empty_id():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_current_step("")


def test_set_current_step_rejects_invalid_index():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_current_step(
            "step-1",
            step_index="0",
        )


def test_clear_current_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_current_step(
        "step-1",
        step_index=0,
    )

    context.clear_current_step()

    assert context.current_step_id is None
    assert context.current_step_index is None


# ============================================================
# Step Results
# ============================================================


def test_record_completed_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.record_completed_step(
        "step-1",
        {
            "value": 42,
        },
    )

    assert context.completed_steps == 1
    assert context.get_result("step-1") == {
        "value": 42,
    }

    assert context.current_step_id is None
    assert context.current_step_index is None


def test_record_failed_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.record_failed_step(
        "step-1",
        "Tool failed",
    )

    assert context.failed_steps == 1

    assert context.get_result(
        "step-1"
    ) == {
        "error": "Tool failed",
    }


def test_record_skipped_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.record_skipped_step(
        "step-1"
    )

    assert context.skipped_steps == 1


def test_record_retried_step():

    context = ExecutionContext(
        "execution-1"
    )

    context.record_retried_step(
        "step-1"
    )

    assert context.retried_steps == 1


def test_set_result():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_result(
        "step-1",
        "result",
    )

    assert context.get_result(
        "step-1"
    ) == "result"


def test_set_result_rejects_invalid_step_id():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_result(
            "",
            "result",
        )


def test_get_result_returns_default():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.get_result(
        "missing",
        "default",
    ) == "default"


# ============================================================
# Defensive Copies
# ============================================================


def test_get_results_returns_defensive_copy():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_result(
        "step-1",
        {
            "value": 42,
        },
    )

    results = context.get_results()

    results["step-1"]["value"] = 999

    assert context.get_result(
        "step-1"
    )["value"] == 42


def test_metadata_returns_defensive_copy():

    context = ExecutionContext(
        "execution-1",
        metadata={
            "config": {
                "value": 42,
            },
        },
    )

    metadata = context.get_all_metadata()

    metadata["config"]["value"] = 999

    assert context.get_metadata(
        "config"
    )["value"] == 42


# ============================================================
# Metadata
# ============================================================


def test_set_metadata():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_metadata(
        "source",
        "test",
    )

    assert context.get_metadata(
        "source"
    ) == "test"


def test_set_metadata_rejects_empty_key():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.set_metadata(
            "",
            "value",
        )


def test_get_metadata_returns_default():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.get_metadata(
        "missing",
        "default",
    ) == "default"


# ============================================================
# Context Queries
# ============================================================


def test_has_result_returns_true_for_existing_result():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_result(
        "step-1",
        "result",
    )

    assert context.has_result(
        "step-1"
    ) is True


def test_has_result_returns_false_for_missing_result():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.has_result(
        "missing"
    ) is False


def test_has_result_rejects_invalid_step_id():

    context = ExecutionContext(
        "execution-1"
    )

    with pytest.raises(ExecutionContextError):
        context.has_result("")


def test_has_failed_steps():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.has_failed_steps() is False

    context.record_failed_step(
        "step-1",
        "failure",
    )

    assert context.has_failed_steps() is True


def test_has_completed_steps():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.has_completed_steps() is False

    context.record_completed_step(
        "step-1",
        "done",
    )

    assert context.has_completed_steps() is True


def test_has_skipped_steps():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.has_skipped_steps() is False

    context.record_skipped_step(
        "step-1"
    )

    assert context.has_skipped_steps() is True


def test_is_finished_for_completed_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.complete()

    assert context.is_finished() is True


def test_is_finished_for_failed_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.fail()

    assert context.is_finished() is True


def test_is_finished_for_cancelled_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()
    context.cancel()

    assert context.is_finished() is True


def test_is_finished_for_created_context():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.is_finished() is False


def test_is_finished_for_running_context():

    context = ExecutionContext(
        "execution-1"
    )

    context.start()

    assert context.is_finished() is False


def test_get_last_result_returns_latest_result():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_result(
        "step-1",
        "first",
    )

    context.set_result(
        "step-2",
        "second",
    )

    assert context.get_last_result() == "second"


def test_get_last_result_returns_default_when_empty():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.get_last_result(
        "default"
    ) == "default"


def test_get_last_result_returns_defensive_copy():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_result(
        "step-1",
        {
            "value": 42,
        },
    )

    result = context.get_last_result()

    result["value"] = 999

    assert context.get_result(
        "step-1"
    )["value"] == 42


def test_get_processed_steps():

    context = ExecutionContext(
        "execution-1"
    )

    context.record_completed_step(
        "step-1",
        "done",
    )

    context.record_failed_step(
        "step-2",
        "failed",
    )

    context.record_skipped_step(
        "step-3"
    )

    assert context.get_processed_steps() == 3


def test_get_remaining_steps():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_total_steps(5)

    context.record_completed_step(
        "step-1",
        "done",
    )

    context.record_failed_step(
        "step-2",
        "failed",
    )

    assert context.get_remaining_steps() == 3


def test_get_remaining_steps_never_negative():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_total_steps(2)

    context.record_completed_step(
        "step-1",
        "done",
    )

    context.record_completed_step(
        "step-2",
        "done",
    )

    context.record_completed_step(
        "step-3",
        "done",
    )

    assert context.get_remaining_steps() == 0


def test_get_processed_steps_matches_progress():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_total_steps(4)

    context.record_completed_step(
        "step-1",
        "done",
    )

    context.record_failed_step(
        "step-2",
        "failed",
    )

    context.record_skipped_step(
        "step-3"
    )

    assert (
        context.get_processed_steps()
        == context.get_progress()["processed_steps"]
    )


# ============================================================
# State
# ============================================================


def test_context_state_helpers():

    context = ExecutionContext(
        "execution-1"
    )

    assert context.is_created()
    assert not context.is_active()

    context.start()

    assert context.is_running()
    assert context.is_active()

    context.pause()

    assert context.is_paused()
    assert context.is_active()

    context.resume()
    context.cancel()

    assert context.is_cancelled()
    assert not context.is_active()


# ============================================================
# Progress
# ============================================================


def test_progress_tracking():

    context = ExecutionContext(
        "execution-1"
    )

    context.set_total_steps(4)

    context.record_completed_step(
        "step-1",
        "done",
    )

    context.record_failed_step(
        "step-2",
        "failed",
    )

    context.record_skipped_step(
        "step-3"
    )

    context.record_retried_step(
        "step-4"
    )

    progress = context.get_progress()

    assert progress["total_steps"] == 4
    assert progress["completed_steps"] == 1
    assert progress["failed_steps"] == 1
    assert progress["skipped_steps"] == 1
    assert progress["retried_steps"] == 1

    assert progress["processed_steps"] == 3
    assert progress["percentage"] == 75.0


def test_progress_is_zero_when_no_total_steps():

    context = ExecutionContext(
        "execution-1"
    )

    progress = context.get_progress()

    assert progress["percentage"] == 0.0


# ============================================================
# Snapshot
# ============================================================


def test_snapshot_contains_complete_context():

    context = ExecutionContext(
        "execution-1",
        plan_id="plan-1",
        agent_id="agent-1",
        metadata={
            "source": "test",
        },
    )

    context.set_total_steps(2)

    context.start()

    context.set_current_step(
        "step-1",
        step_index=0,
    )

    context.record_completed_step(
        "step-1",
        {
            "value": 42,
        },
    )

    snapshot = context.snapshot()

    assert snapshot["execution_id"] == "execution-1"
    assert snapshot["plan_id"] == "plan-1"
    assert snapshot["agent_id"] == "agent-1"

    assert snapshot["status"] == "running"

    assert snapshot["completed_steps"] == 1
    assert snapshot["total_steps"] == 2

    assert snapshot["metadata"]["source"] == "test"

    assert snapshot["results"]["step-1"] == {
        "value": 42,
    }

    assert snapshot["progress"]["percentage"] == 50.0


def test_snapshot_is_defensive():

    context = ExecutionContext(
        "execution-1",
        metadata={
            "nested": {
                "value": 42,
            },
        },
    )

    context.set_result(
        "step-1",
        {
            "value": 100,
        },
    )

    snapshot = context.snapshot()

    snapshot["metadata"]["nested"]["value"] = 999
    snapshot["results"]["step-1"]["value"] = 999

    assert context.get_metadata(
        "nested"
    )["value"] == 42

    assert context.get_result(
        "step-1"
    )["value"] == 100


# ============================================================
# Representation
# ============================================================


def test_execution_context_repr():

    context = ExecutionContext(
        "execution-1",
        plan_id="plan-1",
        agent_id="agent-1",
    )

    representation = repr(
        context
    )

    assert "ExecutionContext" in representation
    assert "execution-1" in representation
    assert "plan-1" in representation
    assert "agent-1" in representation
    assert "created" in representation