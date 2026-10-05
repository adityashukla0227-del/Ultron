"""
Tests for public Permission exports.

v0.96 — Core Platform Hardening
"""

from modules.agent import (
    Permission,
    PermissionRegistry,
    PermissionRegistryError,
    PermissionValidationError,
)


def test_permission_public_export():
    permission = Permission(
        "file_read",
        description="Read files",
    )

    assert permission.name == "file_read"
    assert permission.is_enabled() is True


def test_permission_registry_public_export():
    registry = PermissionRegistry()

    permission = Permission("file_read")

    assert registry.register(permission) is True
    assert registry.get("file_read") is permission


def test_permission_validation_error_public_export():
    try:
        Permission("")
    except PermissionValidationError:
        pass
    else:
        raise AssertionError(
            "PermissionValidationError was not raised."
        )


def test_permission_registry_error_public_export():
    registry = PermissionRegistry()

    try:
        registry.register("invalid")
    except PermissionRegistryError:
        pass
    else:
        raise AssertionError(
            "PermissionRegistryError was not raised."
        )