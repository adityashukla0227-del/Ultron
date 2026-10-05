"""
Tests for Ultron Permission and PermissionRegistry.

v0.96 — Core Platform Hardening
"""

import pytest

from modules.agent.permission import (
    Permission,
    PermissionValidationError,
)
from modules.agent.permission_registry import (
    PermissionRegistry,
    PermissionRegistryError,
)


def test_permission_defaults():
    permission = Permission("file_read")

    assert permission.name == "file_read"
    assert permission.description == ""
    assert permission.enabled is True
    assert permission.metadata == {}


def test_permission_normalizes_name():
    permission = Permission("  FILE_READ  ")

    assert permission.name == "file_read"


def test_permission_stores_metadata_defensively():
    metadata = {"scope": "workspace"}
    permission = Permission("file_read", metadata=metadata)

    metadata["scope"] = "global"

    assert permission.metadata["scope"] == "workspace"

    returned = permission.get_metadata()
    returned["scope"] = "global"

    assert permission.metadata["scope"] == "workspace"


def test_permission_validation():
    permission = Permission(
        "file_read",
        description="Read files",
        metadata={"scope": "workspace"},
    )

    assert permission.validate() is True


def test_permission_enable_disable():
    permission = Permission("file_read")

    permission.disable()
    assert permission.is_enabled() is False

    permission.enable()
    assert permission.is_enabled() is True


def test_permission_update_metadata():
    permission = Permission("file_read")

    permission.update_metadata("scope", "workspace")

    assert permission.get_metadata() == {"scope": "workspace"}


def test_permission_set_metadata():
    permission = Permission("file_read")

    permission.set_metadata({"scope": "workspace"})

    assert permission.get_metadata() == {"scope": "workspace"}


def test_permission_serialization():
    permission = Permission(
        "file_read",
        description="Read files",
        enabled=False,
        metadata={"scope": "workspace"},
    )

    data = permission.to_dict()

    assert data == {
        "name": "file_read",
        "description": "Read files",
        "enabled": False,
        "metadata": {"scope": "workspace"},
    }


def test_permission_from_dict():
    data = {
        "name": "file_read",
        "description": "Read files",
        "enabled": False,
        "metadata": {"scope": "workspace"},
    }

    permission = Permission.from_dict(data)

    assert permission.to_dict() == data


@pytest.mark.parametrize(
    "name",
    ["", "   ", None, 123],
)
def test_permission_rejects_invalid_name(name):
    with pytest.raises(PermissionValidationError):
        Permission(name)


def test_permission_rejects_invalid_description():
    with pytest.raises(PermissionValidationError):
        Permission("file_read", description=123)


def test_permission_rejects_invalid_enabled_state():
    with pytest.raises(PermissionValidationError):
        Permission("file_read", enabled="yes")


def test_permission_rejects_invalid_metadata():
    with pytest.raises(PermissionValidationError):
        Permission("file_read", metadata=[])


def test_permission_rejects_invalid_metadata_key():
    permission = Permission("file_read")

    with pytest.raises(PermissionValidationError):
        permission.update_metadata("", "value")


def test_permission_repr():
    permission = Permission("file_read", enabled=False)

    assert repr(permission) == "Permission(name='file_read', enabled=False)"


def test_registry_starts_empty():
    registry = PermissionRegistry()

    assert registry.count() == 0
    assert len(registry) == 0
    assert registry.list_permissions() == []
    assert registry.list_permission_names() == []


def test_registry_registers_permission():
    registry = PermissionRegistry()
    permission = Permission("file_read")

    assert registry.register(permission) is True
    assert registry.get("file_read") is permission
    assert registry.has("file_read") is True


def test_registry_normalizes_names():
    registry = PermissionRegistry()
    permission = Permission("  FILE_READ  ")

    assert registry.register(permission) is True
    assert registry.has("file_read") is True
    assert registry.has("FILE_READ") is True


def test_registry_rejects_duplicate_permission():
    registry = PermissionRegistry()

    assert registry.register(
        Permission("file_read"),
    ) is True

    assert registry.register(
        Permission("file_read"),
    ) is False

    assert registry.count() == 1


def test_registry_unregisters_permission():
    registry = PermissionRegistry()

    registry.register(
        Permission("file_read"),
    )

    assert registry.unregister("file_read") is True
    assert registry.has("file_read") is False
    assert registry.count() == 0


def test_registry_unregister_missing_permission():
    registry = PermissionRegistry()

    assert registry.unregister("file_read") is False


def test_registry_lists_permissions():
    registry = PermissionRegistry()

    first = Permission("file_read")
    second = Permission("file_write")

    registry.register(first)
    registry.register(second)

    assert registry.list_permissions() == [first, second]
    assert registry.list_permission_names() == [
        "file_read",
        "file_write",
    ]


def test_registry_clear():
    registry = PermissionRegistry()

    registry.register(
        Permission("file_read"),
    )
    registry.register(
        Permission("file_write"),
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.list_permission_names() == []


def test_registry_contains():
    registry = PermissionRegistry()

    registry.register(
        Permission("file_read"),
    )

    assert "file_read" in registry
    assert "file_write" not in registry


def test_registry_repr():
    registry = PermissionRegistry()

    registry.register(
        Permission("file_read"),
    )

    assert repr(registry) == (
        "PermissionRegistry(permissions=['file_read'])"
    )


def test_registry_constructor():
    permissions = [
        Permission("file_read"),
        Permission("file_write"),
    ]

    registry = PermissionRegistry(permissions)

    assert registry.count() == 2
    assert registry.list_permission_names() == [
        "file_read",
        "file_write",
    ]


def test_registry_rejects_invalid_permission():
    registry = PermissionRegistry()

    with pytest.raises(PermissionRegistryError):
        registry.register("not a permission")


def test_registry_get_empty_name():
    registry = PermissionRegistry()

    assert registry.get("") is None


def test_registry_has_empty_name():
    registry = PermissionRegistry()

    assert registry.has("") is False


def test_registry_unregister_empty_name():
    registry = PermissionRegistry()

    with pytest.raises(PermissionRegistryError):
        registry.unregister("")