"""
Ultron Permission Registry

Manages registered authorization permission definitions.

v0.96 — Core Platform Hardening

Responsibilities:
- Register permissions
- Unregister permissions
- Retrieve permissions
- Check permission existence
- List registered permissions
- Clear registered permissions
- Count registered permissions

The PermissionRegistry does NOT:
- Make authorization decisions
- Execute tools
- Evaluate policies
- Classify risk
- Handle approvals
- Handle authentication
"""

from __future__ import annotations

from typing import List, Optional

from modules.agent.permission import Permission


class PermissionRegistryError(Exception):
    """Raised when a permission registry operation fails."""


class PermissionRegistry:
    """
    Central registry for Ultron Permission objects.
    """

    def __init__(
        self,
        permissions: Optional[List[Permission]] = None,
    ) -> None:
        self._permissions: dict[str, Permission] = {}

        for permission in permissions or []:
            self.register(permission)

    # ========================================================
    # Registration
    # ========================================================

    def register(
        self,
        permission: Permission,
    ) -> bool:
        """
        Register a permission.

        Duplicate permission names are rejected.
        """

        if not isinstance(
            permission,
            Permission,
        ):
            raise PermissionRegistryError(
                "Only Permission objects can be registered."
            )

        permission.validate()

        if permission.name in self._permissions:
            return False

        self._permissions[
            permission.name
        ] = permission

        return True

    # ========================================================
    # Unregistration
    # ========================================================

    def unregister(
        self,
        permission_name: str,
    ) -> bool:
        """
        Remove a permission from the registry.
        """

        if not isinstance(
            permission_name,
            str,
        ):
            raise PermissionRegistryError(
                "Permission name must be a string."
            )

        permission_name = permission_name.strip().lower()

        if not permission_name:
            raise PermissionRegistryError(
                "Permission name is required."
            )

        if permission_name not in self._permissions:
            return False

        del self._permissions[
            permission_name
        ]

        return True

    # ========================================================
    # Retrieval
    # ========================================================

    def get(
        self,
        permission_name: str,
    ) -> Optional[Permission]:
        """
        Retrieve a registered permission by name.
        """

        if not isinstance(
            permission_name,
            str,
        ):
            return None

        permission_name = (
            permission_name.strip().lower()
        )

        return self._permissions.get(
            permission_name
        )

    # ========================================================
    # Availability
    # ========================================================

    def has(
        self,
        permission_name: str,
    ) -> bool:
        """
        Check whether a permission is registered.
        """

        if not isinstance(
            permission_name,
            str,
        ):
            return False

        permission_name = (
            permission_name.strip().lower()
        )

        return permission_name in self._permissions

    # ========================================================
    # Listing
    # ========================================================

    def list_permissions(
        self,
    ) -> List[Permission]:
        """
        Return all registered permissions.
        """

        return list(
            self._permissions.values()
        )

    def list_permission_names(
        self,
    ) -> List[str]:
        """
        Return the names of all registered permissions.
        """

        return list(
            self._permissions.keys()
        )

    # ========================================================
    # Registry Management
    # ========================================================

    def clear(self) -> None:
        """
        Remove all registered permissions.
        """

        self._permissions.clear()

    def count(self) -> int:
        """
        Return the number of registered permissions.
        """

        return len(
            self._permissions
        )

    # ========================================================
    # Representation
    # ========================================================

    def __len__(self) -> int:
        """
        Return the number of registered permissions.
        """

        return self.count()

    def __contains__(
        self,
        permission_name: str,
    ) -> bool:
        """
        Support:

            "file_read" in registry
        """

        return self.has(
            permission_name
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"PermissionRegistry("
            f"permissions="
            f"{self.list_permission_names()}"
            f")"
        )


__all__ = [
    "PermissionRegistry",
    "PermissionRegistryError",
]