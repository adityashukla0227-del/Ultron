"""
Ultron Authorization Tests

v0.96 — Core Platform Hardening

Tests:
- AuthorizationRequest validation
- AuthorizationDecision validation
- Permission lookup
- Enabled permission authorization
- Missing permission denial
- Disabled permission denial
- Invalid authorization request handling
- Tool permission mapping authorization
"""

import pytest

from modules.agent.authorization import (
    AuthorizationDecision,
    AuthorizationError,
    AuthorizationRequest,
    AuthorizationService,
)
from modules.agent.permission import Permission
from modules.agent.permission_registry import PermissionRegistry
from modules.agent.tool_permission_mapping import ToolPermissionMapping


def create_registry(*permissions: Permission) -> PermissionRegistry:
    """Create a permission registry for tests."""
    return PermissionRegistry(list(permissions))


class TestAuthorizationRequest:
    """Tests for AuthorizationRequest."""

    def test_valid_request(self):
        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="file_tool",
            permission_name="file_read",
        )

        assert request.agent_id == "agent-1"
        assert request.tool_name == "file_tool"
        assert request.permission_name == "file_read"

    def test_normalizes_tool_and_permission_names(self):
        request = AuthorizationRequest(
            agent_id=" agent-1 ",
            tool_name=" FILE_TOOL ",
            permission_name=" FILE_READ ",
        )

        assert request.agent_id == "agent-1"
        assert request.tool_name == "file_tool"
        assert request.permission_name == "file_read"

    @pytest.mark.parametrize(
        "field,value",
        [
            ("agent_id", ""),
            ("agent_id", "   "),
            ("tool_name", ""),
            ("tool_name", "   "),
            ("permission_name", ""),
            ("permission_name", "   "),
        ],
    )
    def test_rejects_empty_required_fields(self, field, value):
        values = {
            "agent_id": "agent-1",
            "tool_name": "file_tool",
            "permission_name": "file_read",
        }
        values[field] = value

        with pytest.raises(AuthorizationError):
            AuthorizationRequest(**values)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("agent_id", 123),
            ("tool_name", 123),
            ("permission_name", 123),
        ],
    )
    def test_rejects_non_string_required_fields(self, field, value):
        values = {
            "agent_id": "agent-1",
            "tool_name": "file_tool",
            "permission_name": "file_read",
        }
        values[field] = value

        with pytest.raises(AuthorizationError):
            AuthorizationRequest(**values)


class TestAuthorizationDecision:
    """Tests for AuthorizationDecision."""

    def test_allowed_decision(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        decision = AuthorizationDecision(
            allowed=True,
            permission=permission,
            reason="Permission is registered and enabled.",
        )

        assert decision.allowed is True
        assert decision.permission is permission
        assert decision.reason == "Permission is registered and enabled."

    def test_denied_decision_without_permission(self):
        decision = AuthorizationDecision(
            allowed=False,
            permission=None,
            reason="Permission is not registered.",
        )

        assert decision.allowed is False
        assert decision.permission is None
        assert decision.reason == "Permission is not registered."

    def test_rejects_invalid_allowed_state(self):
        with pytest.raises(AuthorizationError):
            AuthorizationDecision(
                allowed="true",
                permission=None,
                reason="Invalid",
            )

    def test_rejects_invalid_permission(self):
        with pytest.raises(AuthorizationError):
            AuthorizationDecision(
                allowed=True,
                permission="file_read",
                reason="Invalid",
            )

    def test_rejects_invalid_reason(self):
        with pytest.raises(AuthorizationError):
            AuthorizationDecision(
                allowed=True,
                permission=None,
                reason=123,
            )


class TestAuthorizationService:
    """Tests for AuthorizationService."""

    def test_authorizes_enabled_permission(self):
        permission = Permission(
            name="file_read",
            description="Read files",
            enabled=True,
        )

        registry = create_registry(permission)
        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="file_tool",
            permission_name="file_read",
        )

        decision = service.authorize(request)

        assert decision.allowed is True
        assert decision.permission is permission
        assert "registered and enabled" in decision.reason

    def test_denies_missing_permission(self):
        registry = PermissionRegistry()
        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="file_tool",
            permission_name="file_read",
        )

        decision = service.authorize(request)

        assert decision.allowed is False
        assert decision.permission is None
        assert "not registered" in decision.reason

    def test_denies_disabled_permission(self):
        permission = Permission(
            name="file_write",
            description="Write files",
            enabled=False,
        )

        registry = create_registry(permission)
        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="file_tool",
            permission_name="file_write",
        )

        decision = service.authorize(request)

        assert decision.allowed is False
        assert decision.permission is permission
        assert "disabled" in decision.reason

    def test_authorization_service_creates_default_registry(self):
        service = AuthorizationService()

        assert isinstance(
            service.permission_registry,
            PermissionRegistry,
        )

    def test_rejects_invalid_request(self):
        service = AuthorizationService()

        with pytest.raises(AuthorizationError):
            service.authorize("invalid-request")

    def test_permission_name_is_normalized_before_lookup(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        registry = create_registry(permission)
        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="FILE_TOOL",
            permission_name=" FILE_READ ",
        )

        decision = service.authorize(request)

        assert decision.allowed is True
        assert decision.permission is permission


class TestAuthorizationIntegration:
    """Basic integration tests for authorization components."""

    def test_registry_permission_flows_into_authorization_decision(self):
        permission = Permission(
            name="web_search",
            description="Perform web searches",
        )

        registry = PermissionRegistry()
        assert registry.register(permission) is True

        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="web_tool",
            permission_name="web_search",
        )

        decision = service.authorize(request)

        assert decision.allowed is True
        assert decision.permission.name == "web_search"

    def test_disabling_permission_changes_authorization_result(self):
        permission = Permission(
            name="shell_execute",
            description="Execute shell commands",
        )

        registry = create_registry(permission)
        service = AuthorizationService(registry)

        request = AuthorizationRequest(
            agent_id="agent-1",
            tool_name="shell_tool",
            permission_name="shell_execute",
        )

        allowed_decision = service.authorize(request)
        assert allowed_decision.allowed is True

        permission.disable()

        denied_decision = service.authorize(request)
        assert denied_decision.allowed is False
        assert "disabled" in denied_decision.reason


class TestAuthorizationTool:
    """Tests for tool-level permission authorization."""

    def test_authorize_tool_allows_single_required_permission(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        registry = create_registry(permission)
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is True
        assert decision.permission is permission
        assert "authorized" in decision.reason

    def test_authorize_tool_denies_missing_permission(self):
        registry = PermissionRegistry()
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is False
        assert decision.permission is None
        assert "not registered" in decision.reason

    def test_authorize_tool_denies_disabled_permission(self):
        permission = Permission(
            name="file_read",
            description="Read files",
            enabled=False,
        )

        registry = create_registry(permission)
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is False
        assert decision.permission is permission
        assert "disabled" in decision.reason

    def test_authorize_tool_allows_multiple_permissions(self):
        read_permission = Permission(
            name="file_read",
            description="Read files",
        )
        write_permission = Permission(
            name="file_write",
            description="Write files",
        )

        registry = create_registry(
            read_permission,
            write_permission,
        )
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read", "file_write"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is True
        assert decision.permission is read_permission

    def test_authorize_tool_denies_when_one_permission_is_disabled(self):
        read_permission = Permission(
            name="file_read",
            description="Read files",
        )
        write_permission = Permission(
            name="file_write",
            description="Write files",
            enabled=False,
        )

        registry = create_registry(
            read_permission,
            write_permission,
        )
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read", "file_write"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is False
        assert decision.permission is write_permission
        assert "disabled" in decision.reason

    def test_authorize_tool_denies_unmapped_tool(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        registry = create_registry(permission)
        mapping = ToolPermissionMapping()
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is False
        assert decision.permission is None
        assert "no permission mapping" in decision.reason

    def test_authorize_tool_denies_empty_permission_mapping(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        registry = create_registry(permission)
        mapping = ToolPermissionMapping(
            {"file_tool": []}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            "file_tool",
            mapping,
        )

        assert decision.allowed is False
        assert decision.permission is None
        assert "no required permissions" in decision.reason

    def test_authorize_tool_normalizes_tool_name(self):
        permission = Permission(
            name="file_read",
            description="Read files",
        )

        registry = create_registry(permission)
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )
        service = AuthorizationService(registry)

        decision = service.authorize_tool(
            "agent-1",
            " FILE_TOOL ",
            mapping,
        )

        assert decision.allowed is True

    def test_authorize_tool_rejects_invalid_agent_id(self):
        service = AuthorizationService()
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )

        with pytest.raises(AuthorizationError):
            service.authorize_tool(
                "",
                "file_tool",
                mapping,
            )

    def test_authorize_tool_rejects_invalid_tool_name(self):
        service = AuthorizationService()
        mapping = ToolPermissionMapping(
            {"file_tool": ["file_read"]}
        )

        with pytest.raises(AuthorizationError):
            service.authorize_tool(
                "agent-1",
                "",
                mapping,
            )

    def test_authorize_tool_rejects_invalid_mapping(self):
        service = AuthorizationService()

        with pytest.raises(AuthorizationError):
            service.authorize_tool(
                "agent-1",
                "file_tool",
                None,
            )
