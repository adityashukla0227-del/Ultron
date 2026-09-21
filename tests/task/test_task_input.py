"""
Ultron Task Input Contract Tests
Version: v0.82
"""

import pytest

from modules.task.task_input import (
    TaskInputContract,
    TaskInputContractError,
)


def test_valid_contract():
    contract = TaskInputContract(
        name="calculator_input",
        description="Calculator task input",
        schema={
            "expression": str,
        },
    )

    assert contract.name == "calculator_input"
    assert contract.description == "Calculator task input"
    assert contract.schema == {
        "expression": str,
    }


def test_default_description():
    contract = TaskInputContract(
        name="test_input",
    )

    assert contract.description == ""


def test_default_schema():
    contract = TaskInputContract(
        name="test_input",
    )

    assert contract.schema == {}


def test_schema_is_defensively_copied_on_initialization():
    schema = {
        "expression": str,
    }

    contract = TaskInputContract(
        name="calculator_input",
        schema=schema,
    )

    schema["value"] = int

    assert contract.schema == {
        "expression": str,
    }


def test_name_must_be_string():
    with pytest.raises(
        TaskInputContractError,
        match="name must be a string",
    ):
        TaskInputContract(
            name=123,
        )


def test_name_must_not_be_empty():
    with pytest.raises(
        TaskInputContractError,
        match="name must not be empty",
    ):
        TaskInputContract(
            name="   ",
        )


def test_description_must_be_string():
    with pytest.raises(
        TaskInputContractError,
        match="description must be a string",
    ):
        TaskInputContract(
            name="test_input",
            description=123,
        )


def test_schema_must_be_dictionary():
    with pytest.raises(
        TaskInputContractError,
        match="schema must be a dictionary",
    ):
        TaskInputContract(
            name="test_input",
            schema=["expression"],
        )


def test_validate_returns_true():
    contract = TaskInputContract(
        name="test_input",
    )

    assert contract.validate() is True


def test_get_schema_returns_defensive_copy():
    contract = TaskInputContract(
        name="calculator_input",
        schema={
            "expression": str,
        },
    )

    schema = contract.get_schema()
    schema["value"] = int

    assert contract.get_schema() == {
        "expression": str,
    }


def test_nested_schema_is_defensively_copied():
    contract = TaskInputContract(
        name="nested_input",
        schema={
            "user": {
                "name": str,
            },
        },
    )

    schema = contract.get_schema()
    schema["user"]["name"] = int

    assert contract.get_schema() == {
        "user": {
            "name": str,
        },
    }


def test_to_dict():
    contract = TaskInputContract(
        name="calculator_input",
        description="Calculator task input",
        schema={
            "expression": str,
        },
    )

    result = contract.to_dict()

    assert result == {
        "name": "calculator_input",
        "description": "Calculator task input",
        "schema": {
            "expression": str,
        },
    }


def test_to_dict_returns_defensive_schema_copy():
    contract = TaskInputContract(
        name="calculator_input",
        schema={
            "expression": str,
        },
    )

    result = contract.to_dict()
    result["schema"]["expression"] = int

    assert contract.get_schema() == {
        "expression": str,
    }


def test_contract_error_is_exception():
    assert issubclass(
        TaskInputContractError,
        Exception,
    )