"""
Ultron Authorization Layer

Provides authorization request and decision models
for Ultron agent operations.

v0.96 — Core Platform Hardening

Responsibilities:
- Represent authorization requests
- Represent authorization decisions
- Evaluate requested permissions
- Use PermissionRegistry for permission lookup
- Enforce enabled permission state
- Authorize tools using tool permission mappings

The Authorization layer does NOT:
- Execute tools
- Select tools
- Classify risk
- Request human approval
- Handle authentication
- Define security policies
- Manage capabilities
- Modify agent execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from modules.agent.permission import Permission
from modules.agent.permission_registry import PermissionRegistry


class AuthorizationError(Exception):
    """Raised when an authorization operation fails."""


@dataclass(frozen=True)
class AuthorizationRequest:
    """Represents a request to authorize an agent operation."""

    agent_id: str
    tool_name: str
    permission_name: str

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise AuthorizationError(
                "Authorization agent_id must be a non-empty string."
            )

        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise AuthorizationError(
                "Authorization tool_name must be a non-empty string."
            )

        if (
            not isinstance(self.permission_name, str)
            or not self.permission_name.strip()
        ):
            raise AuthorizationError(
                "Authorization permission_name must be a non-empty string."
            )

        object.__setattr__(self, "agent_id", self.agent_id.strip())
        object.__setattr__(self, "tool_name", self.tool_name.strip().lower())
        object.__setattr__(
            self,
            "permission_name",
            self.permission_name.strip().lower(),
        )


@dataclass(frozen=True)
class AuthorizationDecision:
    """Represents the result of an authorization evaluation."""

    allowed: bool
    permission: Optional[Permission]
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise AuthorizationError(
                "Authorization decision allowed state must be a boolean."
            )

        if self.permission is not None and not isinstance(
            self.permission,
            Permission,
        ):
            raise AuthorizationError(
                "Authorization decision permission must be a Permission object "
                "or None."
            )

        if not isinstance(self.reason, str):
            raise AuthorizationError(
                "Authorization decision reason must be a string."
            )


class AuthorizationService:
    """Evaluates authorization requests using a PermissionRegistry."""

    def __init__(
        self,
        permission_registry: Optional[PermissionRegistry] = None,
    ) -> None:
        self.permission_registry = (
            permission_registry
            if permission_registry is not None
            else PermissionRegistry()
        )

    def authorize(
        self,
        request: AuthorizationRequest,
    ) -> AuthorizationDecision:
        """Evaluate an authorization request."""

        if not isinstance(request, AuthorizationRequest):
            raise AuthorizationError(
                "Authorization request must be an AuthorizationRequest."
            )

        permission = self.permission_registry.get(
            request.permission_name
        )

        if permission is None:
            return AuthorizationDecision(
                allowed=False,
                permission=None,
                reason=(
                    f"Permission '{request.permission_name}' "
                    "is not registered."
                ),
            )

        if not permission.is_enabled():
            return AuthorizationDecision(
                allowed=False,
                permission=permission,
                reason=(
                    f"Permission '{request.permission_name}' "
                    "is disabled."
                ),
            )

        return AuthorizationDecision(
            allowed=True,
            permission=permission,
            reason=(
                f"Permission '{request.permission_name}' "
                "is registered and enabled."
            ),
        )

    def authorize_tool(
        self,
        agent_id: str,
        tool_name: str,
        tool_permission_mapping: "ToolPermissionMapping",
    ) -> AuthorizationDecision:
        """Authorize a tool using its mapped required permissions."""

        if not isinstance(agent_id, str) or not agent_id.strip():
            raise AuthorizationError(
                "Authorization agent_id must be a non-empty string."
            )

        if not isinstance(tool_name, str) or not tool_name.strip():
            raise AuthorizationError(
                "Authorization tool_name must be a non-empty string."
            )

        from modules.agent.tool_permission_mapping import ToolPermissionMapping

        if not isinstance(
            tool_permission_mapping,
            ToolPermissionMapping,
        ):
            raise AuthorizationError(
                "Tool permission mapping must be a ToolPermissionMapping."
            )

        normalized_agent_id = agent_id.strip()
        normalized_tool_name = tool_name.strip().lower()

        if not tool_permission_mapping.has(normalized_tool_name):
            return AuthorizationDecision(
                allowed=False,
                permission=None,
                reason=(
                    f"Tool '{normalized_tool_name}' "
                    "has no permission mapping."
                ),
            )

        required_permissions = tool_permission_mapping.get_permissions(
            normalized_tool_name
        )

        if not required_permissions:
            return AuthorizationDecision(
                allowed=False,
                permission=None,
                reason=(
                    f"Tool '{normalized_tool_name}' "
                    "has no required permissions."
                ),
            )

        for permission_name in required_permissions:
            request = AuthorizationRequest(
                agent_id=normalized_agent_id,
                tool_name=normalized_tool_name,
                permission_name=permission_name,
            )

            decision = self.authorize(request)

            if not decision.allowed:
                return decision

        permission = self.permission_registry.get(
            required_permissions[0]
        )

        return AuthorizationDecision(
            allowed=True,
            permission=permission,
            reason=(
                f"Tool '{normalized_tool_name}' "
                "is authorized because all required permissions "
                "are registered and enabled."
            ),
        )


__all__ = [
    "AuthorizationRequest",
    "AuthorizationDecision",
    "AuthorizationService",
    "AuthorizationError",
]
