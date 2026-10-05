"""
Ultron Tool Permission Mapping

Defines the relationship between tools and required permissions.

v0.96 — Core Platform Hardening

Responsibilities:
- Register tool-to-permission mappings
- Unregister mappings
- Retrieve required permissions for a tool
- Check mapping existence
- List mapped tools
- Clear mappings

The ToolPermissionMapping does NOT:
- Make authorization decisions
- Execute tools
- Select tools
- Classify risk
- Request approvals
- Handle authentication
- Manage permissions themselves
- Manage capabilities
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional


class ToolPermissionMappingError(Exception):
    """Raised when a tool permission mapping operation fails."""


class ToolPermissionMapping:
    """Maintains tool-to-permission relationships."""

    def __init__(
        self,
        mappings: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self._mappings: Dict[str, List[str]] = {}

        if mappings is not None:
            if not isinstance(mappings, dict):
                raise ToolPermissionMappingError(
                    "Mappings must be a dictionary."
                )

            for tool_name, permissions in mappings.items():
                self.register(tool_name, permissions)

    def register(
        self,
        tool_name: str,
        permissions: List[str],
    ) -> bool:
        """Register required permissions for a tool."""

        if not isinstance(tool_name, str):
            raise ToolPermissionMappingError(
                "Tool name must be a string."
            )

        normalized_tool_name = tool_name.strip().lower()

        if not normalized_tool_name:
            raise ToolPermissionMappingError(
                "Tool name is required."
            )

        if not isinstance(permissions, list):
            raise ToolPermissionMappingError(
                "Permissions must be a list."
            )

        normalized_permissions: List[str] = []

        for permission_name in permissions:
            if not isinstance(permission_name, str):
                raise ToolPermissionMappingError(
                    "Permission names must be strings."
                )

            normalized_permission = permission_name.strip().lower()

            if not normalized_permission:
                raise ToolPermissionMappingError(
                    "Permission names must be non-empty strings."
                )

            if normalized_permission not in normalized_permissions:
                normalized_permissions.append(normalized_permission)

        if normalized_tool_name in self._mappings:
            return False

        self._mappings[normalized_tool_name] = normalized_permissions
        return True

    def unregister(self, tool_name: str) -> bool:
        """Remove a tool permission mapping."""

        if not isinstance(tool_name, str):
            raise ToolPermissionMappingError(
                "Tool name must be a string."
            )

        normalized_tool_name = tool_name.strip().lower()

        if not normalized_tool_name:
            raise ToolPermissionMappingError(
                "Tool name is required."
            )

        if normalized_tool_name not in self._mappings:
            return False

        del self._mappings[normalized_tool_name]
        return True

    def get_permissions(self, tool_name: str) -> List[str]:
        """Return required permissions for a tool."""

        if not isinstance(tool_name, str):
            return []

        normalized_tool_name = tool_name.strip().lower()

        return deepcopy(
            self._mappings.get(normalized_tool_name, [])
        )

    def has(self, tool_name: str) -> bool:
        """Return whether a tool has a permission mapping."""

        if not isinstance(tool_name, str):
            return False

        normalized_tool_name = tool_name.strip().lower()

        return normalized_tool_name in self._mappings

    def list_tools(self) -> List[str]:
        """Return all mapped tool names."""

        return list(self._mappings.keys())

    def clear(self) -> None:
        """Remove all tool permission mappings."""

        self._mappings.clear()

    def count(self) -> int:
        """Return the number of mapped tools."""

        return len(self._mappings)

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, tool_name: str) -> bool:
        return self.has(tool_name)

    def __repr__(self) -> str:
        return (
            "ToolPermissionMapping("
            f"tools={self.list_tools()}"
            ")"
        )


__all__ = [
    "ToolPermissionMapping",
    "ToolPermissionMappingError",
]