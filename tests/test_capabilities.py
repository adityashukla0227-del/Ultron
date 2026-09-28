"""
Tests for Ultron Capability.

v0.93 — Capability Registration
"""

import pytest

from modules.agent.capability import (
    Capability,
    CapabilityValidationError,
)


def test_capability_defaults():
    capability = Capability(
        name="calculation",
    )

    assert capability.name == "calculation"
    assert capability.description == ""
    assert capability.metadata == {}


def test_capability_values_are_trimmed():
    capability = Capability(
        name="  calculation  ",
        description="  Perform calculations.  ",
    )

    assert capability.name == "calculation"
    assert capability.description == "Perform calculations."


def test_capability_metadata_is_copied():
    metadata = {
        "category": "math",
        "version": "1.0",
    }

    capability = Capability(
        name="calculation",
        metadata=metadata,
    )

    assert capability.metadata == metadata
    assert capability.metadata is not metadata


def test_capability_invalid_name_type():
    with pytest.raises(CapabilityValidationError):
        Capability(
            name=123,
        )


def test_capability_empty_name():
    with pytest.raises(CapabilityValidationError):
        Capability(
            name="",
        )


def test_capability_whitespace_name():
    with pytest.raises(CapabilityValidationError):
        Capability(
            name="   ",
        )


def test_capability_invalid_description_type():
    with pytest.raises(CapabilityValidationError):
        Capability(
            name="calculation",
            description=123,
        )


def test_capability_invalid_metadata_type():
    with pytest.raises(CapabilityValidationError):
        Capability(
            name="calculation",
            metadata="invalid",
        )


def test_capability_validate():
    capability = Capability(
        name="calculation",
        description="Perform calculations.",
    )

    assert capability.validate() is True


def test_capability_set_metadata():
    capability = Capability(
        name="calculation",
    )

    capability.set_metadata(
        {
            "category": "math",
        }
    )

    assert capability.metadata == {
        "category": "math",
    }


def test_capability_set_metadata_none():
    capability = Capability(
        name="calculation",
        metadata={
            "category": "math",
        },
    )

    capability.set_metadata(None)

    assert capability.metadata == {}


def test_capability_set_metadata_invalid():
    capability = Capability(
        name="calculation",
    )

    with pytest.raises(CapabilityValidationError):
        capability.set_metadata("invalid")


def test_capability_update_metadata():
    capability = Capability(
        name="calculation",
        metadata={
            "category": "math",
        },
    )

    capability.update_metadata(
        {
            "version": "1.0",
        }
    )

    assert capability.metadata == {
        "category": "math",
        "version": "1.0",
    }


def test_capability_update_metadata_overwrites_existing():
    capability = Capability(
        name="calculation",
        metadata={
            "version": "1.0",
        },
    )

    capability.update_metadata(
        {
            "version": "2.0",
        }
    )

    assert capability.metadata == {
        "version": "2.0",
    }


def test_capability_update_metadata_invalid():
    capability = Capability(
        name="calculation",
    )

    with pytest.raises(CapabilityValidationError):
        capability.update_metadata("invalid")


def test_capability_get_metadata_returns_copy():
    capability = Capability(
        name="calculation",
        metadata={
            "category": "math",
        },
    )

    metadata = capability.get_metadata()

    metadata["category"] = "changed"
    metadata["new"] = True

    assert capability.metadata == {
        "category": "math",
    }


def test_capability_to_dict():
    capability = Capability(
        name="calculation",
        description="Perform calculations.",
        metadata={
            "category": "math",
        },
    )

    assert capability.to_dict() == {
        "name": "calculation",
        "description": "Perform calculations.",
        "metadata": {
            "category": "math",
        },
    }


def test_capability_to_dict_returns_metadata_copy():
    capability = Capability(
        name="calculation",
        metadata={
            "category": "math",
        },
    )

    data = capability.to_dict()

    data["metadata"]["category"] = "changed"

    assert capability.metadata == {
        "category": "math",
    }


def test_capability_from_dict():
    capability = Capability.from_dict(
        {
            "name": "calculation",
            "description": "Perform calculations.",
            "metadata": {
                "category": "math",
            },
        }
    )

    assert capability.name == "calculation"
    assert capability.description == "Perform calculations."
    assert capability.metadata == {
        "category": "math",
    }


def test_capability_from_dict_defaults():
    capability = Capability.from_dict(
        {
            "name": "calculation",
        }
    )

    assert capability.name == "calculation"
    assert capability.description == ""
    assert capability.metadata == {}


def test_capability_from_dict_invalid_data():
    with pytest.raises(CapabilityValidationError):
        Capability.from_dict(
            "invalid",
        )


def test_capability_from_dict_invalid_metadata():
    with pytest.raises(CapabilityValidationError):
        Capability.from_dict(
            {
                "name": "calculation",
                "metadata": "invalid",
            }
        )


def test_capability_repr():
    capability = Capability(
        name="calculation",
        description="Perform calculations.",
    )

    representation = repr(capability)

    assert "Capability" in representation
    assert "calculation" in representation
    assert "Perform calculations." in representation