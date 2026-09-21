"""
Ultron Task Output Contract Tests
Version: v0.82
"""

import pytest

from modules.task.task_output import (
    TaskOutputContract,
    TaskOutputContractError,
)


def test_valid_contract():
    contract = TaskOutputContract(
        name="calculator_output",
        description="Calculator task output",
        schema={
            "value": float,
        },
    )

    assert contract.name == "calculator_output"
    assert contract.description == "Calculator task output"
    assert contract.schema == {
        "value": float,
    }


def test_default_description():
    contract = TaskOutputContract(
        name="test_output",
    )

    assert contract.description == ""


def test_default_schema():
    contract = TaskOutputContract(
        name="test_output",
    )

    assert contract.schema == {}


def test_schema_is_defensively_copied_on_initialization():
    schema = {
        "value": float,
    }

    contract = TaskOutputContract(
        name="calculator_output",
        schema=schema,
    )

    schema["error"] = str

    assert contract.schema == {
        "value": float,
    }


def test_name_must_be_string():
    with pytest.raises(
        TaskOutputContractError,
        match="name must be a string",
    ):
        TaskOutputContract(
            name=123,
        )


def test_name_must_not_be_empty():
    with pytest.raises(
        TaskOutputContractError,
        match="name must not be empty",
    ):
        TaskOutputContract(
            name="   ",
        )


def test_description_must_be_string():
    with pytest.raises(
        TaskOutputContractError,
        match="description must be a string",
    ):
        TaskOutputContract(
            name="test_output",
            description=123,
        )


def test_schema_must_be_dictionary():
    with pytest.raises(
        TaskOutputContractError,
        match="schema must be a dictionary",
    ):
        TaskOutputContract(
            name="test_output",
            schema=["value"],
        )


def test_validate_returns_true():
    contract = TaskOutputContract(
        name="test_output",
    )

    assert contract.validate() is True


def test_get_schema_returns_defensive_copy():
    contract = TaskOutputContract(
        name="calculator_output",
        schema={
            "value": float,
        },
    )

    schema = contract.get_schema()
    schema["error"] = str

    assert contract.get_schema() == {
        "value": float,
    }


def test_nested_schema_is_defensively_copied():
    contract = TaskOutputContract(
        name="nested_output",
        schema={
            "result": {
                "value": float,
            },
        },
    )

    schema = contract.get_schema()
    schema["result"]["value"] = str

    assert contract.get_schema() == {
        "result": {
            "value": float,
        },
    }


def test_to_dict():
    contract = TaskOutputContract(
        name="calculator_output",
        description="Calculator task output",
        schema={
            "value": float,
        },
    )

    result = contract.to_dict()

    assert result == {
        "name": "calculator_output",
        "description": "Calculator task output",
        "schema": {
            "value": float,
        },
    }


def test_to_dict_returns_defensive_schema_copy():
    contract = TaskOutputContract(
        name="calculator_output",
        schema={
            "value": float,
        },
    )

    result = contract.to_dict()
    result["schema"]["value"] = int

    assert contract.get_schema() == {
        "value": float,
    }


def test_contract_error_is_exception():
    assert issubclass(
        TaskOutputContractError,
        Exception,
    )