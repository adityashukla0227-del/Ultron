"""
Tests for Ultron Execution Feedback Adapter.
Version: v0.84
"""

from copy import deepcopy

import pytest

from modules.agent.execution_feedback import ExecutionFeedback
from modules.agent.execution_feedback_adapter import (
    ExecutionFeedbackAdapter,
    ExecutionFeedbackAdapterError,
)
from modules.agent.execution_result import ExecutionResult


def test_converts_successful_execution_result():
    result = ExecutionResult(
        execution_id="exec-001",
        success=True,
        result={"value": 42},
        error=None,
        metadata={
            "plan_id": "plan-001",
            "agent_id": "agent-001",
            "progress": {
                "completed": 2,
                "total": 3,
            },
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert isinstance(feedback, ExecutionFeedback)
    assert feedback.execution_id == "exec-001"
    assert feedback.status == "completed"
    assert feedback.message is None
    assert feedback.result == {"value": 42}
    assert feedback.error is None
    assert feedback.progress == {
        "completed": 2,
        "total": 3,
    }
    assert feedback.metadata == {
        "plan_id": "plan-001",
        "agent_id": "agent-001",
    }


def test_converts_failed_execution_result():
    result = ExecutionResult(
        execution_id="exec-002",
        success=False,
        result=None,
        error="Tool execution failed.",
        metadata={
            "plan_id": "plan-002",
            "agent_id": "agent-002",
            "progress": {
                "completed": 1,
                "total": 3,
            },
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.execution_id == "exec-002"
    assert feedback.status == "failed"
    assert feedback.result is None
    assert feedback.error == "Tool execution failed."
    assert feedback.progress == {
        "completed": 1,
        "total": 3,
    }
    assert feedback.metadata == {
        "plan_id": "plan-002",
        "agent_id": "agent-002",
    }


def test_preserves_execution_result_data():
    result_data = {
        "answer": "completed",
        "items": [1, 2, 3],
    }

    result = ExecutionResult(
        execution_id="exec-003",
        success=True,
        result=result_data,
        metadata={},
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.result == result_data


def test_extracts_progress_from_metadata():
    result = ExecutionResult(
        execution_id="exec-004",
        success=True,
        result="done",
        metadata={
            "progress": {
                "current_step": 4,
                "total_steps": 5,
            },
            "plan_id": "plan-004",
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.progress == {
        "current_step": 4,
        "total_steps": 5,
    }

    assert feedback.metadata == {
        "plan_id": "plan-004",
    }


def test_progress_is_removed_from_feedback_metadata():
    result = ExecutionResult(
        execution_id="exec-005",
        success=True,
        result="done",
        metadata={
            "progress": {
                "current": 1,
            },
            "plan_id": "plan-005",
            "custom": "value",
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert "progress" not in feedback.metadata
    assert feedback.metadata == {
        "plan_id": "plan-005",
        "custom": "value",
    }


def test_missing_progress_defaults_to_empty_dictionary():
    result = ExecutionResult(
        execution_id="exec-006",
        success=True,
        result="done",
        metadata={
            "plan_id": "plan-006",
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.progress == {}
    assert feedback.metadata == {
        "plan_id": "plan-006",
    }


def test_none_progress_defaults_to_empty_dictionary():
    result = ExecutionResult(
        execution_id="exec-007",
        success=True,
        result="done",
        metadata={
            "progress": None,
            "plan_id": "plan-007",
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.progress == {}
    assert feedback.metadata == {
        "plan_id": "plan-007",
    }


def test_preserves_non_progress_metadata():
    result = ExecutionResult(
        execution_id="exec-008",
        success=True,
        result="done",
        metadata={
            "plan_id": "plan-008",
            "agent_id": "agent-008",
            "custom": {
                "source": "test",
            },
            "progress": {
                "completed": 3,
            },
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.metadata == {
        "plan_id": "plan-008",
        "agent_id": "agent-008",
        "custom": {
            "source": "test",
        },
    }


def test_metadata_is_defensively_copied():
    metadata = {
        "plan_id": "plan-009",
        "nested": {
            "value": 10,
        },
        "progress": {
            "completed": 1,
        },
    }

    result = ExecutionResult(
        execution_id="exec-009",
        success=True,
        result="done",
        metadata=metadata,
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    metadata["plan_id"] = "changed"
    metadata["nested"]["value"] = 99

    assert feedback.metadata["plan_id"] == "plan-009"
    assert feedback.metadata["nested"]["value"] == 10


def test_progress_is_defensively_copied():
    progress = {
        "completed": 2,
        "nested": {
            "value": 10,
        },
    }

    result = ExecutionResult(
        execution_id="exec-010",
        success=True,
        result="done",
        metadata={
            "progress": progress,
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    progress["completed"] = 99
    progress["nested"]["value"] = 100

    assert feedback.progress["completed"] == 2
    assert feedback.progress["nested"]["value"] == 10


def test_result_is_defensively_copied():
    result_data = {
        "items": [
            "a",
            "b",
        ],
        "nested": {
            "value": 10,
        },
    }

    result = ExecutionResult(
        execution_id="exec-011",
        success=True,
        result=result_data,
        metadata={},
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    result_data["items"].append("c")
    result_data["nested"]["value"] = 99

    assert feedback.result == {
        "items": [
            "a",
            "b",
        ],
        "nested": {
            "value": 10,
        },
    }


def test_feedback_is_valid():
    result = ExecutionResult(
        execution_id="exec-012",
        success=True,
        result="done",
        metadata={
            "progress": {
                "completed": 1,
            },
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.validate() is True


def test_adapter_does_not_modify_execution_result_metadata():
    metadata = {
        "plan_id": "plan-013",
        "progress": {
            "completed": 2,
        },
    }

    result = ExecutionResult(
        execution_id="exec-013",
        success=True,
        result="done",
        metadata=deepcopy(metadata),
    )

    original_metadata = deepcopy(result.metadata)

    ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert result.metadata == original_metadata


def test_adapter_does_not_modify_execution_result_result():
    result_data = {
        "value": 42,
        "nested": {
            "value": 10,
        },
    }

    result = ExecutionResult(
        execution_id="exec-014",
        success=True,
        result=result_data,
        metadata={},
    )

    original_result = deepcopy(result.result)

    ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert result.result == original_result


def test_rejects_non_execution_result():
    with pytest.raises(
        ExecutionFeedbackAdapterError,
        match="result must be an ExecutionResult",
    ):
        ExecutionFeedbackAdapter.from_execution_result(
            "invalid"
        )


def test_rejects_none_result():
    with pytest.raises(
        ExecutionFeedbackAdapterError,
        match="result must be an ExecutionResult",
    ):
        ExecutionFeedbackAdapter.from_execution_result(
            None
        )


def test_rejects_execution_result_with_invalid_progress_metadata():
    result = ExecutionResult(
        execution_id="exec-016",
        success=True,
        result="done",
        metadata={
            "progress": "invalid-progress",
        },
    )

    with pytest.raises(
        ExecutionFeedbackAdapterError,
        match="progress metadata must be a dictionary",
    ):
        ExecutionFeedbackAdapter.from_execution_result(
            result
        )


def test_handles_empty_metadata():
    result = ExecutionResult(
        execution_id="exec-017",
        success=True,
        result="done",
        metadata={},
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.progress == {}
    assert feedback.metadata == {}


def test_handles_complex_execution_result():
    result = ExecutionResult(
        execution_id="exec-018",
        success=True,
        result={
            "steps": [
                {
                    "id": "step-1",
                    "output": {
                        "value": 100,
                    },
                },
                {
                    "id": "step-2",
                    "output": {
                        "value": 200,
                    },
                },
            ],
        },
        metadata={
            "plan_id": "plan-018",
            "agent_id": "agent-018",
            "progress": {
                "completed": 2,
                "total": 2,
                "percentage": 100,
            },
            "source": "orchestrator",
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.execution_id == "exec-018"
    assert feedback.status == "completed"
    assert feedback.progress["completed"] == 2
    assert feedback.progress["total"] == 2
    assert feedback.progress["percentage"] == 100
    assert feedback.metadata == {
        "plan_id": "plan-018",
        "agent_id": "agent-018",
        "source": "orchestrator",
    }


def test_failed_execution_preserves_error():
    result = ExecutionResult(
        execution_id="exec-019",
        success=False,
        result=None,
        error="Execution failed because the tool timed out.",
        metadata={
            "progress": {
                "completed": 0,
                "total": 1,
            },
        },
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.status == "failed"
    assert feedback.error == (
        "Execution failed because the tool timed out."
    )


def test_successful_execution_has_no_error():
    result = ExecutionResult(
        execution_id="exec-020",
        success=True,
        result="success",
        error=None,
        metadata={},
    )

    feedback = ExecutionFeedbackAdapter.from_execution_result(
        result
    )

    assert feedback.status == "completed"
    assert feedback.error is None