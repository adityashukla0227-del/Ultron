"""
Ultron Task Contract Tests
Version: v0.82
"""

import pytest

from modules.task.task import (
    Task,
    TaskType,
)
from modules.task.task_contract import (
    TaskContract,
    TaskContractError,
)
from modules.task.task_input import (
    TaskInputContract,
)
from modules.task.task_output import (
    TaskOutputContract,
)


def create_task() -> Task:
    return Task(
        task_id="task-001",
        task_type=TaskType.ACTION,
        description="Calculate a value",
    )


def create_input_contract() -> TaskInputContract:
    return TaskInputContract(
        name="calculator_input",
        description="Calculator input",
        schema={
            "expression": str,
        },
    )


def create_output_contract() -> TaskOutputContract:
    return TaskOutputContract(
        name="calculator_output",
        description="Calculator output",
        schema={
            "value": float,
        },
    )


def create_contract() -> TaskContract:
    return TaskContract(
        task=create_task(),
        input_contract=create_input_contract(),
        output_contract=create_output_contract(),
    )


def test_valid_contract():
    contract = create_contract()

    assert contract.task.task_id == "task-001"
    assert (
        contract.input_contract.name
        == "calculator_input"
    )
    assert (
        contract.output_contract.name
        == "calculator_output"
    )


def test_task_must_be_task_instance():
    with pytest.raises(
        TaskContractError,
        match="task must be a Task instance",
    ):
        TaskContract(
            task="invalid",
            input_contract=create_input_contract(),
            output_contract=create_output_contract(),
        )


def test_input_contract_must_be_task_input_contract():
    with pytest.raises(
        TaskContractError,
        match="input_contract must be a TaskInputContract",
    ):
        TaskContract(
            task=create_task(),
            input_contract="invalid",
            output_contract=create_output_contract(),
        )


def test_output_contract_must_be_task_output_contract():
    with pytest.raises(
        TaskContractError,
        match="output_contract must be a TaskOutputContract",
    ):
        TaskContract(
            task=create_task(),
            input_contract=create_input_contract(),
            output_contract="invalid",
        )


def test_validate_returns_true():
    contract = create_contract()

    assert contract.validate() is True


def test_get_input_contract():
    contract = create_contract()

    result = contract.get_input_contract()

    assert result is contract.input_contract
    assert result.name == "calculator_input"


def test_get_output_contract():
    contract = create_contract()

    result = contract.get_output_contract()

    assert result is contract.output_contract
    assert result.name == "calculator_output"


def test_to_dict():
    contract = create_contract()

    result = contract.to_dict()

    assert result == {
        "task": {
            "task_id": "task-001",
            "task_type": "action",
            "description": "Calculate a value",
            "source": "unknown",
            "metadata": {},
        },
        "input_contract": {
            "name": "calculator_input",
            "description": "Calculator input",
            "schema": {
                "expression": str,
            },
        },
        "output_contract": {
            "name": "calculator_output",
            "description": "Calculator output",
            "schema": {
                "value": float,
            },
        },
    }


def test_to_dict_returns_defensive_nested_copy():
    contract = create_contract()

    result = contract.to_dict()

    result["input_contract"]["schema"]["expression"] = int
    result["output_contract"]["schema"]["value"] = str

    assert (
        contract.input_contract.get_schema()
        == {
            "expression": str,
        }
    )

    assert (
        contract.output_contract.get_schema()
        == {
            "value": float,
        }
    )


def test_contract_error_is_exception():
    assert issubclass(
        TaskContractError,
        Exception,
    )