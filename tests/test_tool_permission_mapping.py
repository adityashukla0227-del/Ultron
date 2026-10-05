"""
Ultron Tool Permission Mapping Tests

v0.96 — Core Platform Hardening
"""

import pytest

from modules.agent.tool_permission_mapping import (
    ToolPermissionMapping,
    ToolPermissionMappingError,
)


class TestToolPermissionMapping:
    """Tests for ToolPermissionMapping."""

    def test_register_mapping(self):
        mapping = ToolPermissionMapping()

        result = mapping.register(
            "file_tool",
            ["file.read"],
        )

        assert result is True
        assert mapping.get_permissions("file_tool") == ["file.read"]

    def test_register_multiple_permissions(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            [
                "file.read",
                "file.write",
            ],
        )

        assert mapping.get_permissions("file_tool") == [
            "file.read",
            "file.write",
        ]

    def test_normalizes_tool_and_permission_names(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            " FILE_TOOL ",
            [
                " FILE.READ ",
                " FILE.WRITE ",
            ],
        )

        assert mapping.has("file_tool")
        assert mapping.get_permissions("file_tool") == [
            "file.read",
            "file.write",
        ]

    def test_removes_duplicate_permissions(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            [
                "file.read",
                "file.read",
                "FILE.READ",
            ],
        )

        assert mapping.get_permissions("file_tool") == [
            "file.read",
        ]

    def test_duplicate_tool_mapping_returns_false(self):
        mapping = ToolPermissionMapping()

        assert mapping.register(
            "file_tool",
            ["file.read"],
        ) is True

        assert mapping.register(
            "file_tool",
            ["file.write"],
        ) is False

        assert mapping.get_permissions("file_tool") == [
            "file.read",
        ]

    def test_missing_tool_returns_empty_permissions(self):
        mapping = ToolPermissionMapping()

        assert mapping.get_permissions("unknown_tool") == []

    def test_has_returns_false_for_missing_tool(self):
        mapping = ToolPermissionMapping()

        assert mapping.has("unknown_tool") is False

    def test_unregister_mapping(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            ["file.read"],
        )

        assert mapping.unregister("file_tool") is True
        assert mapping.has("file_tool") is False
        assert mapping.get_permissions("file_tool") == []

    def test_unregister_missing_mapping_returns_false(self):
        mapping = ToolPermissionMapping()

        assert mapping.unregister("unknown_tool") is False

    def test_get_permissions_returns_defensive_copy(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            [
                "file.read",
                "file.write",
            ],
        )

        permissions = mapping.get_permissions("file_tool")
        permissions.append("shell.execute")

        assert mapping.get_permissions("file_tool") == [
            "file.read",
            "file.write",
        ]

    def test_constructor_accepts_mappings(self):
        mapping = ToolPermissionMapping(
            {
                "file_tool": ["file.read"],
                "web_tool": ["web.search"],
            }
        )

        assert mapping.get_permissions("file_tool") == [
            "file.read",
        ]

        assert mapping.get_permissions("web_tool") == [
            "web.search",
        ]

    def test_constructor_rejects_non_dictionary(self):
        with pytest.raises(ToolPermissionMappingError):
            ToolPermissionMapping([])

    def test_register_rejects_non_string_tool_name(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.register(
                123,
                ["file.read"],
            )

    def test_register_rejects_empty_tool_name(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.register(
                "   ",
                ["file.read"],
            )

    def test_register_rejects_non_list_permissions(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.register(
                "file_tool",
                "file.read",
            )

    def test_register_rejects_non_string_permission(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.register(
                "file_tool",
                [123],
            )

    def test_register_rejects_empty_permission_name(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.register(
                "file_tool",
                ["   "],
            )

    def test_unregister_rejects_non_string_tool_name(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.unregister(123)

    def test_unregister_rejects_empty_tool_name(self):
        mapping = ToolPermissionMapping()

        with pytest.raises(ToolPermissionMappingError):
            mapping.unregister("   ")

    def test_list_tools(self):
        mapping = ToolPermissionMapping()

        mapping.register("file_tool", ["file.read"])
        mapping.register("web_tool", ["web.search"])

        assert mapping.list_tools() == [
            "file_tool",
            "web_tool",
        ]

    def test_clear(self):
        mapping = ToolPermissionMapping()

        mapping.register("file_tool", ["file.read"])
        mapping.register("web_tool", ["web.search"])

        mapping.clear()

        assert mapping.list_tools() == []
        assert mapping.count() == 0

    def test_count_and_len(self):
        mapping = ToolPermissionMapping()

        assert mapping.count() == 0
        assert len(mapping) == 0

        mapping.register("file_tool", ["file.read"])
        mapping.register("web_tool", ["web.search"])

        assert mapping.count() == 2
        assert len(mapping) == 2

    def test_contains(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            ["file.read"],
        )

        assert "file_tool" in mapping
        assert "unknown_tool" not in mapping

    def test_repr(self):
        mapping = ToolPermissionMapping()

        mapping.register(
            "file_tool",
            ["file.read"],
        )

        representation = repr(mapping)

        assert "ToolPermissionMapping" in representation
        assert "file_tool" in representation