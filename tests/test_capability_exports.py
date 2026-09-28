"""
Tests for Ultron capability public exports.

v0.93 — Capability Registration
"""

from modules.agent import (
    Capability,
    CapabilityRegistry,
    CapabilityRegistryError,
    CapabilityValidationError,
)


def test_capability_public_exports():
    capability = Capability(
        name="calculation",
        description="Perform calculations.",
    )

    registry = CapabilityRegistry()

    assert isinstance(
        capability,
        Capability,
    )

    assert isinstance(
        registry,
        CapabilityRegistry,
    )


def test_capability_error_exports():
    assert issubclass(
        CapabilityValidationError,
        Exception,
    )

    assert issubclass(
        CapabilityRegistryError,
        Exception,
    )


def test_capability_registry_public_workflow():
    capability = Capability(
        name="file_read",
        description="Read files.",
    )

    registry = CapabilityRegistry()

    assert registry.register(
        capability
    ) is True

    assert registry.has(
        "file_read"
    ) is True

    assert registry.get(
        "file_read"
    ) is capability