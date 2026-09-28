"""
Tests for Ultron Capability Registry.

v0.93 — Capability Registration
"""

import pytest

from modules.agent.capability import Capability
from modules.agent.capability_registry import (
    CapabilityRegistry,
    CapabilityRegistryError,
)
from modules.agent.tool import AgentTool


def test_registry_defaults():
    registry = CapabilityRegistry()

    assert registry.list_capabilities() == []
    assert registry.list_capability_names() == []
    assert registry.count() == 0
    assert len(registry) == 0


def test_registry_initializes_with_capabilities():
    calculation = Capability(
        name="calculation",
    )

    file_read = Capability(
        name="file_read",
    )

    registry = CapabilityRegistry(
        capabilities=[
            calculation,
            file_read,
        ]
    )

    assert registry.count() == 2
    assert registry.has("calculation")
    assert registry.has("file_read")


def test_register_capability():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculation",
    )

    assert registry.register(
        capability
    ) is True

    assert registry.get(
        "calculation"
    ) is capability


def test_register_duplicate_capability():
    registry = CapabilityRegistry()

    first = Capability(
        name="calculation",
    )

    second = Capability(
        name="calculation",
        description="Different description",
    )

    assert registry.register(first) is True
    assert registry.register(second) is False

    assert registry.get(
        "calculation"
    ) is first

    assert registry.count() == 1


def test_register_invalid_capability():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.register(
            "invalid"
        )


def test_unregister_capability():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculation",
    )

    registry.register(capability)

    assert registry.unregister(
        "calculation"
    ) is True

    assert registry.has(
        "calculation"
    ) is False

    assert registry.count() == 0


def test_unregister_missing_capability():
    registry = CapabilityRegistry()

    assert registry.unregister(
        "missing"
    ) is False


def test_unregister_invalid_name():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.unregister(
            123
        )


def test_get_capability():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculation",
    )

    registry.register(capability)

    assert registry.get(
        "calculation"
    ) is capability


def test_get_capability_trims_name():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculation",
    )

    registry.register(capability)

    assert registry.get(
        "  calculation  "
    ) is capability


def test_get_missing_capability():
    registry = CapabilityRegistry()

    assert registry.get(
        "missing"
    ) is None


def test_get_invalid_name():
    registry = CapabilityRegistry()

    assert registry.get(
        123
    ) is None


def test_has_capability():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    assert registry.has(
        "calculation"
    ) is True

    assert registry.has(
        "missing"
    ) is False


def test_has_capability_trims_name():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    assert registry.has(
        "  calculation  "
    ) is True


def test_has_invalid_name():
    registry = CapabilityRegistry()

    assert registry.has(
        123
    ) is False


def test_list_capabilities():
    registry = CapabilityRegistry()

    calculation = Capability(
        name="calculation",
    )

    file_read = Capability(
        name="file_read",
    )

    registry.register(calculation)
    registry.register(file_read)

    capabilities = registry.list_capabilities()

    assert capabilities == [
        calculation,
        file_read,
    ]


def test_list_capabilities_returns_new_list():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculation",
    )

    registry.register(capability)

    capabilities = registry.list_capabilities()

    capabilities.clear()

    assert registry.count() == 1
    assert registry.has(
        "calculation"
    )


def test_list_capability_names():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    registry.register(
        Capability(
            name="file_read",
        )
    )

    assert registry.list_capability_names() == [
        "calculation",
        "file_read",
    ]


def test_list_capability_names_returns_new_list():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    names = registry.list_capability_names()

    names.clear()

    assert registry.count() == 1
    assert registry.has(
        "calculation"
    )


def test_get_tools_for_capability():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    unrelated = AgentTool(
        name="text_tool",
        capabilities=[
            "text_processing",
        ],
    )

    tools = registry.get_tools_for_capability(
        "calculation",
        [
            calculator,
            unrelated,
        ],
    )

    assert tools == [
        calculator,
    ]


def test_get_tools_for_capability_multiple_tools():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    advanced_calculator = AgentTool(
        name="advanced_calculator",
        capabilities=[
            "calculation",
            "statistics",
        ],
    )

    tools = registry.get_tools_for_capability(
        "calculation",
        [
            calculator,
            advanced_calculator,
        ],
    )

    assert tools == [
        calculator,
        advanced_calculator,
    ]


def test_get_tools_for_capability_trims_name():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    tools = registry.get_tools_for_capability(
        "  calculation  ",
        [
            calculator,
        ],
    )

    assert tools == [
        calculator,
    ]


def test_get_tools_for_capability_missing_capability():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    assert registry.get_tools_for_capability(
        "missing",
        [
            calculator,
        ],
    ) == []


def test_get_tools_for_capability_invalid_name():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.get_tools_for_capability(
            123,
            [],
        )


def test_get_tools_for_capability_empty_name():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.get_tools_for_capability(
            "   ",
            [],
        )


def test_get_tools_for_capability_invalid_tools_type():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.get_tools_for_capability(
            "calculation",
            "invalid",
        )


def test_get_tools_for_capability_invalid_tool():
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityRegistryError):
        registry.get_tools_for_capability(
            "calculation",
            [
                "invalid",
            ],
        )


def test_get_tools_for_capability_does_not_mutate_tools():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    original_capabilities = calculator.get_capabilities()

    registry.get_tools_for_capability(
        "calculation",
        [
            calculator,
        ],
    )

    assert calculator.get_capabilities() == (
        original_capabilities
    )


def test_clear_registry():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    registry.register(
        Capability(
            name="file_read",
        )
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.list_capabilities() == []
    assert registry.list_capability_names() == []


def test_registry_contains():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    assert "calculation" in registry
    assert "missing" not in registry


def test_registry_repr():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="calculation",
        )
    )

    representation = repr(registry)

    assert "CapabilityRegistry" in representation
    assert "calculation" in representation