"""
Ultron Plugin Architecture Tests
Version: v0.92

Focused tests for:
- Plugin
- PluginRegistry
"""

import pytest

from modules.agent.plugin import (
    Plugin,
    PluginValidationError,
)
from modules.agent.plugin_registry import (
    PluginRegistry,
    PluginRegistryError,
)
from modules.agent.tool import AgentTool


# ============================================================
# Plugin Construction
# ============================================================


def test_plugin_defaults() -> None:
    plugin = Plugin(
        name="calculator",
    )

    assert plugin.name == "calculator"
    assert plugin.version == "1.0"
    assert plugin.description == ""
    assert plugin.tools == []
    assert plugin.metadata == {}


def test_plugin_custom_configuration() -> None:
    tool = AgentTool(
        name="add",
        description="Add numbers",
    )

    plugin = Plugin(
        name="calculator",
        version="2.0",
        description="Calculator plugin",
        tools=[tool],
        metadata={
            "author": "Ultron",
            "category": "utility",
        },
    )

    assert plugin.name == "calculator"
    assert plugin.version == "2.0"
    assert plugin.description == "Calculator plugin"
    assert plugin.get_tools() == [tool]
    assert plugin.metadata == {
        "author": "Ultron",
        "category": "utility",
    }


# ============================================================
# Plugin Validation
# ============================================================


def test_plugin_requires_name() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(name="")


def test_plugin_requires_string_name() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(name=123)


def test_plugin_requires_version() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(
            name="calculator",
            version="",
        )


def test_plugin_requires_string_version() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(
            name="calculator",
            version=123,
        )


def test_plugin_requires_string_description() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(
            name="calculator",
            description=123,
        )


def test_plugin_tools_must_be_agent_tools() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(
            name="calculator",
            tools=["invalid"],
        )


def test_plugin_metadata_must_be_dictionary() -> None:
    with pytest.raises(PluginValidationError):
        Plugin(
            name="calculator",
            metadata="invalid",
        )


# ============================================================
# Plugin Tool Management
# ============================================================


def test_plugin_add_tool() -> None:
    plugin = Plugin(
        name="calculator",
    )

    tool = AgentTool(
        name="add",
    )

    assert plugin.add_tool(tool) is True
    assert plugin.get_tool("add") is tool
    assert plugin.get_tools() == [tool]


def test_plugin_duplicate_tool_is_ignored() -> None:
    plugin = Plugin(
        name="calculator",
    )

    first = AgentTool(
        name="add",
    )

    second = AgentTool(
        name="add",
    )

    assert plugin.add_tool(first) is True
    assert plugin.add_tool(second) is False
    assert plugin.get_tools() == [first]


def test_plugin_add_tool_requires_agent_tool() -> None:
    plugin = Plugin(
        name="calculator",
    )

    with pytest.raises(PluginValidationError):
        plugin.add_tool("invalid")  # type: ignore[arg-type]


def test_plugin_get_missing_tool() -> None:
    plugin = Plugin(
        name="calculator",
    )

    assert plugin.get_tool("missing") is None


def test_plugin_remove_tool() -> None:
    tool = AgentTool(
        name="add",
    )

    plugin = Plugin(
        name="calculator",
        tools=[tool],
    )

    assert plugin.remove_tool("add") is True
    assert plugin.get_tool("add") is None


def test_plugin_remove_missing_tool() -> None:
    plugin = Plugin(
        name="calculator",
    )

    assert plugin.remove_tool("missing") is False


def test_plugin_remove_tool_requires_string_name() -> None:
    plugin = Plugin(
        name="calculator",
    )

    with pytest.raises(PluginValidationError):
        plugin.remove_tool(123)  # type: ignore[arg-type]


def test_plugin_get_tools_returns_copy() -> None:
    tool = AgentTool(
        name="add",
    )

    plugin = Plugin(
        name="calculator",
        tools=[tool],
    )

    tools = plugin.get_tools()
    tools.clear()

    assert plugin.get_tools() == [tool]


# ============================================================
# Plugin Metadata
# ============================================================


def test_plugin_metadata_get_returns_copy() -> None:
    plugin = Plugin(
        name="calculator",
        metadata={
            "category": "utility",
        },
    )

    metadata = plugin.get_metadata()
    metadata["category"] = "changed"

    assert plugin.metadata["category"] == "utility"


def test_plugin_set_metadata() -> None:
    plugin = Plugin(
        name="calculator",
    )

    plugin.set_metadata(
        {
            "category": "utility",
        }
    )

    assert plugin.metadata == {
        "category": "utility",
    }


def test_plugin_set_metadata_none() -> None:
    plugin = Plugin(
        name="calculator",
        metadata={
            "category": "utility",
        },
    )

    plugin.set_metadata(None)

    assert plugin.metadata == {}


def test_plugin_set_metadata_requires_dictionary() -> None:
    plugin = Plugin(
        name="calculator",
    )

    with pytest.raises(PluginValidationError):
        plugin.set_metadata("invalid")  # type: ignore[arg-type]


def test_plugin_update_metadata() -> None:
    plugin = Plugin(
        name="calculator",
        metadata={
            "category": "utility",
        },
    )

    plugin.update_metadata(
        {
            "author": "Ultron",
        }
    )

    assert plugin.metadata == {
        "category": "utility",
        "author": "Ultron",
    }


def test_plugin_update_metadata_requires_dictionary() -> None:
    plugin = Plugin(
        name="calculator",
    )

    with pytest.raises(PluginValidationError):
        plugin.update_metadata("invalid")  # type: ignore[arg-type]


# ============================================================
# Plugin Serialization
# ============================================================


def test_plugin_to_dict() -> None:
    tool = AgentTool(
        name="add",
        description="Add numbers",
    )

    plugin = Plugin(
        name="calculator",
        version="2.0",
        description="Calculator plugin",
        tools=[tool],
        metadata={
            "category": "utility",
        },
    )

    data = plugin.to_dict()

    assert data["name"] == "calculator"
    assert data["version"] == "2.0"
    assert data["description"] == "Calculator plugin"
    assert data["metadata"] == {
        "category": "utility",
    }
    assert len(data["tools"]) == 1
    assert data["tools"][0]["name"] == "add"


def test_plugin_from_dict() -> None:
    data = {
        "name": "calculator",
        "version": "2.0",
        "description": "Calculator plugin",
        "tools": [
            {
                "name": "add",
                "description": "Add numbers",
            }
        ],
        "metadata": {
            "category": "utility",
        },
    }

    plugin = Plugin.from_dict(data)

    assert plugin.name == "calculator"
    assert plugin.version == "2.0"
    assert plugin.description == "Calculator plugin"
    assert plugin.get_tool("add") is not None
    assert plugin.get_tool("add").name == "add"
    assert plugin.metadata == {
        "category": "utility",
    }


def test_plugin_from_dict_requires_dictionary() -> None:
    with pytest.raises(PluginValidationError):
        Plugin.from_dict([])  # type: ignore[arg-type]


def test_plugin_from_dict_requires_tool_dictionaries() -> None:
    with pytest.raises(PluginValidationError):
        Plugin.from_dict(
            {
                "name": "calculator",
                "tools": ["invalid"],
            }
        )


def test_plugin_repr() -> None:
    tool = AgentTool(
        name="add",
    )

    plugin = Plugin(
        name="calculator",
        version="2.0",
        tools=[tool],
    )

    representation = repr(plugin)

    assert "Plugin(" in representation
    assert "calculator" in representation
    assert "2.0" in representation
    assert "add" in representation


# ============================================================
# Plugin Registry
# ============================================================


def test_plugin_registry_defaults() -> None:
    registry = PluginRegistry()

    assert registry.count() == 0
    assert len(registry) == 0
    assert registry.list_plugins() == []
    assert registry.list_plugin_names() == []


def test_plugin_registry_register() -> None:
    registry = PluginRegistry()

    plugin = Plugin(
        name="calculator",
    )

    assert registry.register(plugin) is True
    assert registry.get("calculator") is plugin
    assert registry.has("calculator") is True
    assert registry.count() == 1


def test_plugin_registry_duplicate_registration() -> None:
    registry = PluginRegistry()

    first = Plugin(
        name="calculator",
    )

    second = Plugin(
        name="calculator",
    )

    assert registry.register(first) is True
    assert registry.register(second) is False
    assert registry.get("calculator") is first


def test_plugin_registry_requires_plugin() -> None:
    registry = PluginRegistry()

    with pytest.raises(PluginRegistryError):
        registry.register("invalid")  # type: ignore[arg-type]


def test_plugin_registry_unregister() -> None:
    registry = PluginRegistry()

    plugin = Plugin(
        name="calculator",
    )

    registry.register(plugin)

    assert registry.unregister("calculator") is True
    assert registry.get("calculator") is None
    assert registry.has("calculator") is False
    assert registry.count() == 0


def test_plugin_registry_unregister_missing() -> None:
    registry = PluginRegistry()

    assert registry.unregister("missing") is False


def test_plugin_registry_unregister_requires_string_name() -> None:
    registry = PluginRegistry()

    with pytest.raises(PluginRegistryError):
        registry.unregister(123)  # type: ignore[arg-type]


def test_plugin_registry_get_invalid_name() -> None:
    registry = PluginRegistry()

    assert registry.get(123) is None  # type: ignore[arg-type]


def test_plugin_registry_has_invalid_name() -> None:
    registry = PluginRegistry()

    assert registry.has(123) is False  # type: ignore[arg-type]


def test_plugin_registry_lists_plugins() -> None:
    registry = PluginRegistry()

    first = Plugin(
        name="calculator",
    )

    second = Plugin(
        name="browser",
    )

    registry.register(first)
    registry.register(second)

    assert registry.list_plugins() == [
        first,
        second,
    ]

    assert registry.list_plugin_names() == [
        "calculator",
        "browser",
    ]


def test_plugin_registry_clear() -> None:
    registry = PluginRegistry()

    registry.register(
        Plugin(
            name="calculator",
        )
    )

    registry.register(
        Plugin(
            name="browser",
        )
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.list_plugins() == []
    assert registry.list_plugin_names() == []


def test_plugin_registry_contains() -> None:
    registry = PluginRegistry()

    registry.register(
        Plugin(
            name="calculator",
        )
    )

    assert "calculator" in registry
    assert "missing" not in registry


def test_plugin_registry_repr() -> None:
    registry = PluginRegistry()

    registry.register(
        Plugin(
            name="calculator",
        )
    )

    representation = repr(registry)

    assert "PluginRegistry(" in representation
    assert "calculator" in representation