"""Tests for the v0.88 execution recovery model and planner."""

import pytest

from modules.agent.execution_failure import (
    ExecutionFailure,
    FailureCategory,
    FailureScope,
)
from modules.agent.execution_recovery import (
    ExecutionRecovery,
    ExecutionRecoveryPlanner,
    RecoveryAction,
)
from modules.agent.execution_state_snapshot import (
    ExecutionStateSnapshot,
)


def create_snapshot(
    *,
    execution_id="exec-1",
    status="running",
    current_step_id="step-1",
    current_step_index=0,
):
    return ExecutionStateSnapshot(
        execution_id=execution_id,
        status=status,
        current_step_id=current_step_id,
        current_step_index=current_step_index,
        completed_steps=0,
        failed_steps=0,
        pending_steps=1,
        retry_count=0,
    )


def create_failure(
    *,
    execution_id="exec-1",
    step_id="step-1",
    retryable=True,
    scope=FailureScope.STEP,
):
    return ExecutionFailure(
        execution_id=execution_id,
        scope=scope,
        category=FailureCategory.STEP_FAILURE,
        message="Step execution failed.",
        retryable=retryable,
        step_id=step_id,
    )


# ---------------------------------------------------------------------------
# ExecutionRecovery model tests
# ---------------------------------------------------------------------------


def test_create_resume_recovery():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.RESUME,
        reason="Execution can resume from its preserved state.",
    )

    assert recovery.execution_id == "exec-1"
    assert recovery.action is RecoveryAction.RESUME
    assert recovery.reason == "Execution can resume from its preserved state."
    assert recovery.step_id is None


def test_create_retry_recovery():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.RETRY,
        reason="The failed step is retryable.",
        step_id="step-1",
    )

    assert recovery.action is RecoveryAction.RETRY
    assert recovery.step_id == "step-1"


def test_create_skip_recovery():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.SKIP,
        reason="The step may be skipped.",
        step_id="step-1",
    )

    assert recovery.action is RecoveryAction.SKIP
    assert recovery.step_id == "step-1"


def test_create_abort_recovery():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.ABORT,
        reason="Recovery is not possible.",
    )

    assert recovery.action is RecoveryAction.ABORT
    assert recovery.step_id is None


def test_recovery_is_immutable():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.RESUME,
        reason="Resume execution.",
    )

    with pytest.raises(AttributeError):
        recovery.action = RecoveryAction.ABORT


def test_to_dict():
    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.RETRY,
        reason="Retry the failed step.",
        step_id="step-1",
        metadata={"attempt": 2},
    )

    assert recovery.to_dict() == {
        "execution_id": "exec-1",
        "action": "retry",
        "reason": "Retry the failed step.",
        "step_id": "step-1",
        "metadata": {"attempt": 2},
    }


def test_to_dict_defensively_copies_metadata():
    metadata = {"attempt": 2}

    recovery = ExecutionRecovery(
        execution_id="exec-1",
        action=RecoveryAction.RETRY,
        reason="Retry the failed step.",
        step_id="step-1",
        metadata=metadata,
    )

    serialized = recovery.to_dict()
    serialized["metadata"]["attempt"] = 99

    assert recovery.metadata == {"attempt": 2}


def test_retry_requires_step_id():
    with pytest.raises(ValueError):
        ExecutionRecovery(
            execution_id="exec-1",
            action=RecoveryAction.RETRY,
            reason="Retry failed step.",
        )


def test_skip_requires_step_id():
    with pytest.raises(ValueError):
        ExecutionRecovery(
            execution_id="exec-1",
            action=RecoveryAction.SKIP,
            reason="Skip failed step.",
        )


def test_invalid_execution_id():
    with pytest.raises(ValueError):
        ExecutionRecovery(
            execution_id="",
            action=RecoveryAction.ABORT,
            reason="Abort execution.",
        )


def test_invalid_reason():
    with pytest.raises(ValueError):
        ExecutionRecovery(
            execution_id="exec-1",
            action=RecoveryAction.ABORT,
            reason="",
        )


def test_invalid_action_type():
    with pytest.raises(TypeError):
        ExecutionRecovery(
            execution_id="exec-1",
            action="resume",
            reason="Resume execution.",
        )


# ---------------------------------------------------------------------------
# ExecutionRecoveryPlanner tests
# ---------------------------------------------------------------------------


def test_planner_resumes_paused_execution():
    snapshot = create_snapshot(
        status="paused",
        current_step_id="step-2",
        current_step_index=1,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot)

    assert recovery.action is RecoveryAction.RESUME
    assert recovery.execution_id == "exec-1"
    assert recovery.step_id == "step-2"


def test_planner_retries_retryable_current_step():
    snapshot = create_snapshot(
        status="running",
        current_step_id="step-1",
        current_step_index=0,
    )

    failure = create_failure(
        step_id="step-1",
        retryable=True,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot, failure)

    assert recovery.action is RecoveryAction.RETRY
    assert recovery.execution_id == "exec-1"
    assert recovery.step_id == "step-1"


def test_planner_aborts_non_retryable_failure():
    snapshot = create_snapshot(
        status="running",
    )

    failure = create_failure(
        step_id="step-1",
        retryable=False,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot, failure)

    assert recovery.action is RecoveryAction.ABORT
    assert recovery.step_id is None


def test_planner_aborts_when_failed_step_does_not_match_current_step():
    snapshot = create_snapshot(
        status="running",
        current_step_id="step-2",
    )

    failure = create_failure(
        step_id="step-1",
        retryable=True,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot, failure)

    assert recovery.action is RecoveryAction.ABORT


def test_planner_aborts_running_execution_without_failure():
    snapshot = create_snapshot(
        status="running",
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot)

    assert recovery.action is RecoveryAction.ABORT


def test_planner_aborts_failed_execution():
    snapshot = create_snapshot(
        status="failed",
        current_step_id=None,
        current_step_index=None,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot)

    assert recovery.action is RecoveryAction.ABORT


def test_planner_rejects_invalid_snapshot_type():
    planner = ExecutionRecoveryPlanner()

    with pytest.raises(TypeError):
        planner.plan("invalid")


def test_planner_rejects_invalid_failure_type():
    snapshot = create_snapshot()

    planner = ExecutionRecoveryPlanner()

    with pytest.raises(TypeError):
        planner.plan(snapshot, "invalid")


def test_planner_rejects_mismatched_execution_id():
    snapshot = create_snapshot(
        execution_id="exec-1",
    )

    failure = create_failure(
        execution_id="exec-2",
    )

    planner = ExecutionRecoveryPlanner()

    with pytest.raises(ValueError):
        planner.plan(snapshot, failure)


def test_planner_aborts_execution_scoped_failure():
    snapshot = create_snapshot(
        status="running",
    )

    failure = ExecutionFailure(
        execution_id="exec-1",
        scope=FailureScope.EXECUTION,
        category=FailureCategory.EXECUTION_FAILURE,
        message="Execution failed.",
        retryable=True,
    )

    planner = ExecutionRecoveryPlanner()
    recovery = planner.plan(snapshot, failure)

    assert recovery.action is RecoveryAction.ABORT
    assert recovery.step_id is None