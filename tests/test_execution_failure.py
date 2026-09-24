"""
Tests for Ultron Execution Failure Model.

v0.87 — Failure Handling Foundation
"""

import pytest

from modules.agent.execution_failure import (
    ExecutionFailure,
    FailureCategory,
    FailureScope,
)


def test_execution_failure_creation():
    failure = ExecutionFailure(
        execution_id="exec-001",
        scope=FailureScope.STEP,
        category=FailureCategory.EXCEPTION,
        message="Tool execution failed",
        retryable=True,
        step_id="step-001",
    )

    assert failure.execution_id == "exec-001"
    assert failure.scope is FailureScope.STEP
    assert failure.category is FailureCategory.EXCEPTION
    assert failure.message == "Tool execution failed"
    assert failure.retryable is True
    assert failure.step_id == "step-001"


def test_execution_failure_is_immutable():
    failure = ExecutionFailure(
        execution_id="exec-001",
        scope=FailureScope.EXECUTION,
        category=FailureCategory.EXECUTION_FAILURE,
        message="Execution failed",
        retryable=False,
    )

    with pytest.raises((AttributeError, TypeError)):
        failure.message = "changed"


def test_execution_failure_to_dict():
    failure = ExecutionFailure(
        execution_id="exec-001",
        scope=FailureScope.STEP,
        category=FailureCategory.TOOL_FAILURE,
        message="Tool failed",
        retryable=True,
        step_id="step-001",
        metadata={"tool": "calculator"},
    )

    result = failure.to_dict()

    assert result == {
        "execution_id": "exec-001",
        "scope": "step",
        "category": "tool_failure",
        "message": "Tool failed",
        "retryable": True,
        "step_id": "step-001",
        "metadata": {"tool": "calculator"},
    }


def test_metadata_is_defensively_serialized():
    metadata = {"tool": "calculator"}

    failure = ExecutionFailure(
        execution_id="exec-001",
        scope=FailureScope.STEP,
        category=FailureCategory.TOOL_FAILURE,
        message="Tool failed",
        retryable=True,
        step_id="step-001",
        metadata=metadata,
    )

    result = failure.to_dict()
    result["metadata"]["tool"] = "changed"

    assert failure.metadata == {"tool": "calculator"}


def test_step_failure_requires_step_id():
    with pytest.raises(ValueError):
        ExecutionFailure(
            execution_id="exec-001",
            scope=FailureScope.STEP,
            category=FailureCategory.STEP_FAILURE,
            message="Step failed",
            retryable=True,
        )


def test_execution_failure_rejects_step_id():
    with pytest.raises(ValueError):
        ExecutionFailure(
            execution_id="exec-001",
            scope=FailureScope.EXECUTION,
            category=FailureCategory.EXECUTION_FAILURE,
            message="Execution failed",
            retryable=False,
            step_id="step-001",
        )


def test_invalid_execution_id_is_rejected():
    with pytest.raises(ValueError):
        ExecutionFailure(
            execution_id="",
            scope=FailureScope.EXECUTION,
            category=FailureCategory.UNKNOWN,
            message="Unknown failure",
            retryable=False,
        )


def test_invalid_message_is_rejected():
    with pytest.raises(ValueError):
        ExecutionFailure(
            execution_id="exec-001",
            scope=FailureScope.EXECUTION,
            category=FailureCategory.UNKNOWN,
            message="",
            retryable=False,
        )


def test_invalid_retryable_type_is_rejected():
    with pytest.raises(TypeError):
        ExecutionFailure(
            execution_id="exec-001",
            scope=FailureScope.EXECUTION,
            category=FailureCategory.UNKNOWN,
            message="Failure",
            retryable="yes",
        )