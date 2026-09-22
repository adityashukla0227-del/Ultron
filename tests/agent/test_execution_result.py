"""
Tests for Ultron ExecutionResult.

Version: v0.83
"""

import pytest

from modules.agent.execution_result import (
    ExecutionResult,
    ExecutionResultError,
)


def test_execution_result_creation():
    result = ExecutionResult(
        execution_id="execution-001",
        success=True,
        result={"value": 42},
    )

    assert result.execution_id == "execution-001"
    assert result.success is True
    assert result.result == {"value": 42}
    assert result.error is None
    assert result.metadata == {}


def test_execution_result_failure():
    result = ExecutionResult(
        execution_id="execution-002",
        success=False,
        result=None,
        error="Execution failed.",
    )

    assert result.execution_id == "execution-002"
    assert result.success is False
    assert result.result is None
    assert result.error == "Execution failed."


def test_execution_result_metadata():
    result = ExecutionResult(
        execution_id="execution-003",
        success=True,
        result=100,
        metadata={
            "task_id": "task-001",
            "agent_id": "agent-001",
        },
    )

    assert result.metadata == {
        "task_id": "task-001",
        "agent_id": "agent-001",
    }


def test_execution_result_metadata_is_defensively_copied():
    metadata = {
        "task_id": "task-001",
        "nested": {
            "value": 10,
        },
    }

    result = ExecutionResult(
        execution_id="execution-004",
        success=True,
        metadata=metadata,
    )

    metadata["task_id"] = "modified"
    metadata["nested"]["value"] = 99

    assert result.metadata["task_id"] == "task-001"
    assert result.metadata["nested"]["value"] == 10


def test_execution_result_to_dict():
    result = ExecutionResult(
        execution_id="execution-005",
        success=True,
        result={"value": 42},
        metadata={"source": "test"},
    )

    serialized = result.to_dict()

    assert serialized == {
        "execution_id": "execution-005",
        "success": True,
        "result": {"value": 42},
        "error": None,
        "metadata": {"source": "test"},
    }


def test_execution_result_to_dict_is_defensive():
    result = ExecutionResult(
        execution_id="execution-006",
        success=True,
        result={
            "nested": {
                "value": 10,
            },
        },
        metadata={
            "source": "test",
        },
    )

    serialized = result.to_dict()

    serialized["result"]["nested"]["value"] = 99
    serialized["metadata"]["source"] = "modified"

    assert result.result["nested"]["value"] == 10
    assert result.metadata["source"] == "test"


def test_execution_result_validate():
    result = ExecutionResult(
        execution_id="execution-007",
        success=True,
        result="completed",
    )

    assert result.validate() is True


def test_execution_result_is_immutable():
    result = ExecutionResult(
        execution_id="execution-008",
        success=True,
        result="completed",
    )

    with pytest.raises(AttributeError):
        result.success = False


def test_invalid_execution_id_type():
    with pytest.raises(
        ExecutionResultError,
        match="execution_id must be a string",
    ):
        ExecutionResult(
            execution_id=123,
            success=True,
        )


def test_empty_execution_id():
    with pytest.raises(
        ExecutionResultError,
        match="execution_id must not be empty",
    ):
        ExecutionResult(
            execution_id="   ",
            success=True,
        )


def test_invalid_success_type():
    with pytest.raises(
        ExecutionResultError,
        match="success must be a boolean",
    ):
        ExecutionResult(
            execution_id="execution-009",
            success="true",
        )


def test_invalid_error_type():
    with pytest.raises(
        ExecutionResultError,
        match="error must be a string or None",
    ):
        ExecutionResult(
            execution_id="execution-010",
            success=False,
            error=123,
        )


def test_invalid_metadata_type():
    with pytest.raises(
        ExecutionResultError,
        match="metadata must be a dictionary or None",
    ):
        ExecutionResult(
            execution_id="execution-011",
            success=True,
            metadata="invalid",
        )


def test_none_metadata_becomes_empty_dictionary():
    result = ExecutionResult(
        execution_id="execution-012",
        success=True,
        metadata=None,
    )

    assert result.metadata == {}


def test_result_can_contain_arbitrary_data():
    result = ExecutionResult(
        execution_id="execution-013",
        success=True,
        result=[
            "step-1",
            {
                "value": 100,
            },
            42,
        ],
    )

    assert result.result == [
        "step-1",
        {
            "value": 100,
        },
        42,
    ]