"""
Tests for Ultron ExecutionFeedback.

Version: v0.84
"""

import pytest

from modules.agent.execution_feedback import (
    ExecutionFeedback,
    ExecutionFeedbackError,
)


def test_execution_feedback_creation():
    feedback = ExecutionFeedback(
        execution_id="execution-001",
        status="completed",
        message="Execution completed.",
        result={"value": 42},
    )

    assert feedback.execution_id == "execution-001"
    assert feedback.status == "completed"
    assert feedback.message == "Execution completed."
    assert feedback.progress == {}
    assert feedback.result == {"value": 42}
    assert feedback.error is None
    assert feedback.metadata == {}


def test_execution_feedback_failure():
    feedback = ExecutionFeedback(
        execution_id="execution-002",
        status="failed",
        message="Execution failed.",
        error="Tool execution failed.",
    )

    assert feedback.execution_id == "execution-002"
    assert feedback.status == "failed"
    assert feedback.message == "Execution failed."
    assert feedback.error == "Tool execution failed."


def test_execution_feedback_progress():
    feedback = ExecutionFeedback(
        execution_id="execution-003",
        status="running",
        progress={
            "completed": 2,
            "total": 5,
        },
    )

    assert feedback.progress == {
        "completed": 2,
        "total": 5,
    }


def test_execution_feedback_metadata():
    feedback = ExecutionFeedback(
        execution_id="execution-004",
        status="completed",
        metadata={
            "task_id": "task-001",
            "agent_id": "agent-001",
        },
    )

    assert feedback.metadata == {
        "task_id": "task-001",
        "agent_id": "agent-001",
    }


def test_execution_feedback_progress_is_defensively_copied():
    progress = {
        "completed": 2,
        "nested": {
            "value": 10,
        },
    }

    feedback = ExecutionFeedback(
        execution_id="execution-005",
        status="running",
        progress=progress,
    )

    progress["completed"] = 99
    progress["nested"]["value"] = 100

    assert feedback.progress["completed"] == 2
    assert feedback.progress["nested"]["value"] == 10


def test_execution_feedback_metadata_is_defensively_copied():
    metadata = {
        "source": "test",
        "nested": {
            "value": 10,
        },
    }

    feedback = ExecutionFeedback(
        execution_id="execution-006",
        status="completed",
        metadata=metadata,
    )

    metadata["source"] = "modified"
    metadata["nested"]["value"] = 99

    assert feedback.metadata["source"] == "test"
    assert feedback.metadata["nested"]["value"] == 10


def test_execution_feedback_result_is_defensively_copied():
    result = {
        "value": 42,
        "nested": {
            "status": "completed",
        },
    }

    feedback = ExecutionFeedback(
        execution_id="execution-007",
        status="completed",
        result=result,
    )

    result["value"] = 99
    result["nested"]["status"] = "modified"

    assert feedback.result["value"] == 42
    assert feedback.result["nested"]["status"] == "completed"


def test_execution_feedback_to_dict():
    feedback = ExecutionFeedback(
        execution_id="execution-008",
        status="completed",
        message="Done.",
        progress={
            "completed": 5,
            "total": 5,
        },
        result={"value": 42},
        error=None,
        metadata={"source": "test"},
    )

    serialized = feedback.to_dict()

    assert serialized == {
        "execution_id": "execution-008",
        "status": "completed",
        "message": "Done.",
        "progress": {
            "completed": 5,
            "total": 5,
        },
        "result": {"value": 42},
        "error": None,
        "metadata": {"source": "test"},
    }


def test_execution_feedback_to_dict_is_defensive():
    feedback = ExecutionFeedback(
        execution_id="execution-009",
        status="completed",
        progress={
            "nested": {
                "value": 10,
            },
        },
        result={
            "nested": {
                "value": 20,
            },
        },
        metadata={
            "nested": {
                "value": 30,
            },
        },
    )

    serialized = feedback.to_dict()

    serialized["progress"]["nested"]["value"] = 99
    serialized["result"]["nested"]["value"] = 99
    serialized["metadata"]["nested"]["value"] = 99

    assert feedback.progress["nested"]["value"] == 10
    assert feedback.result["nested"]["value"] == 20
    assert feedback.metadata["nested"]["value"] == 30


def test_execution_feedback_validate():
    feedback = ExecutionFeedback(
        execution_id="execution-010",
        status="completed",
        result="completed",
    )

    assert feedback.validate() is True


def test_execution_feedback_is_immutable():
    feedback = ExecutionFeedback(
        execution_id="execution-011",
        status="completed",
    )

    with pytest.raises(AttributeError):
        feedback.status = "failed"


def test_invalid_execution_id_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="execution_id must be a string",
    ):
        ExecutionFeedback(
            execution_id=123,
            status="completed",
        )


def test_empty_execution_id():
    with pytest.raises(
        ExecutionFeedbackError,
        match="execution_id must not be empty",
    ):
        ExecutionFeedback(
            execution_id="   ",
            status="completed",
        )


def test_invalid_status_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="status must be a string",
    ):
        ExecutionFeedback(
            execution_id="execution-012",
            status=123,
        )


def test_empty_status():
    with pytest.raises(
        ExecutionFeedbackError,
        match="status must not be empty",
    ):
        ExecutionFeedback(
            execution_id="execution-013",
            status="   ",
        )


def test_invalid_message_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="message must be a string or None",
    ):
        ExecutionFeedback(
            execution_id="execution-014",
            status="completed",
            message=123,
        )


def test_invalid_progress_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="progress must be a dictionary or None",
    ):
        ExecutionFeedback(
            execution_id="execution-015",
            status="running",
            progress="invalid",
        )


def test_invalid_error_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="error must be a string or None",
    ):
        ExecutionFeedback(
            execution_id="execution-016",
            status="failed",
            error=123,
        )


def test_invalid_metadata_type():
    with pytest.raises(
        ExecutionFeedbackError,
        match="metadata must be a dictionary or None",
    ):
        ExecutionFeedback(
            execution_id="execution-017",
            status="completed",
            metadata="invalid",
        )


def test_none_progress_becomes_empty_dictionary():
    feedback = ExecutionFeedback(
        execution_id="execution-018",
        status="running",
        progress=None,
    )

    assert feedback.progress == {}


def test_none_metadata_becomes_empty_dictionary():
    feedback = ExecutionFeedback(
        execution_id="execution-019",
        status="completed",
        metadata=None,
    )

    assert feedback.metadata == {}


def test_execution_feedback_result_can_contain_arbitrary_data():
    feedback = ExecutionFeedback(
        execution_id="execution-020",
        status="completed",
        result=[
            "step-1",
            {
                "value": 100,
            },
            42,
        ],
    )

    assert feedback.result == [
        "step-1",
        {
            "value": 100,
        },
        42,
    ]