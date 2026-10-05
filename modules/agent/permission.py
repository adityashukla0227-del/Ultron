"""
Ultron Permission Model

Defines authorization permission metadata for Ultron.

v0.96 — Core Platform Hardening

Responsibilities:
- Store permission identity
- Store permission description
- Track enabled state
- Store permission metadata
- Validate permission configuration
- Serialize permission configuration
- Restore permission configuration

The Permission model does NOT:
- Make authorization decisions
- Execute tools
- Evaluate policies
- Classify risk
- Request approvals
- Handle authentication
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class PermissionValidationError(ValueError):
    """Raised when a permission contains invalid configuration."""


class Permission:
    """Represents a single authorization permission definition."""

    def __init__(
        self,
        name: str,
        description: str = "",
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(name, str):
            raise PermissionValidationError("Permission name must be a string.")

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise PermissionValidationError(
                "Permission name must be a non-empty string."
            )

        if not isinstance(description, str):
            raise PermissionValidationError(
                "Permission description must be a string."
            )

        if not isinstance(enabled, bool):
            raise PermissionValidationError(
                "Permission enabled state must be a boolean."
            )

        if metadata is not None and not isinstance(metadata, dict):
            raise PermissionValidationError(
                "Permission metadata must be a dictionary."
            )

        self.name = normalized_name
        self.description = description
        self.enabled = enabled
        self.metadata: dict[str, Any] = deepcopy(metadata or {})

    def validate(self) -> bool:
        """Validate the current permission configuration."""

        if not isinstance(self.name, str) or not self.name.strip():
            raise PermissionValidationError(
                "Permission name must be a non-empty string."
            )

        if not isinstance(self.description, str):
            raise PermissionValidationError(
                "Permission description must be a string."
            )

        if not isinstance(self.enabled, bool):
            raise PermissionValidationError(
                "Permission enabled state must be a boolean."
            )

        if not isinstance(self.metadata, dict):
            raise PermissionValidationError(
                "Permission metadata must be a dictionary."
            )

        return True

    def enable(self) -> None:
        """Enable the permission."""

        self.enabled = True

    def disable(self) -> None:
        """Disable the permission."""

        self.enabled = False

    def is_enabled(self) -> bool:
        """Return whether the permission is enabled."""

        return self.enabled

    def get_metadata(self) -> dict[str, Any]:
        """Return a defensive copy of permission metadata."""

        return deepcopy(self.metadata)

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        """Replace permission metadata."""

        if not isinstance(metadata, dict):
            raise PermissionValidationError(
                "Permission metadata must be a dictionary."
            )

        self.metadata = deepcopy(metadata)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update a single metadata entry."""

        if not isinstance(key, str) or not key.strip():
            raise PermissionValidationError(
                "Permission metadata key must be a non-empty string."
            )

        self.metadata[key] = deepcopy(value)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the permission configuration."""

        self.validate()

        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Permission:
        """Restore a permission from serialized configuration."""

        if not isinstance(data, dict):
            raise PermissionValidationError(
                "Permission data must be a dictionary."
            )

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Return a useful debug representation."""

        return (
            f"Permission("
            f"name={self.name!r}, "
            f"enabled={self.enabled!r}"
            f")"
        )