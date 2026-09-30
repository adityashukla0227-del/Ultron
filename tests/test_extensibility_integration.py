"""
Ultron Extensibility Integration Tests
Version: v0.95

Tests:
- Plugin -> AgentTool integration
- Capability -> AgentTool integration
- CapabilityRegistry -> Tool mapping
- ToolRegistry -> Tool registration
- Cross-registry consistency
- Public extensibility exports
"""

from modules.agent import (
    AgentTool,
    Capability,
    CapabilityRegistry,
    Plugin,
    ToolRegistry,
)


def test_plugin_provides_tool_with_capability():
    tool = AgentTool(
        name="calculator",
        description="Performs calculations",
        capabilities=[
            "calculation",
        ],
    )

    plugin = Plugin(
        name="math_plugin",
        version="1.0",
        description="Math tools",
        tools=[
            tool,
        ],
    )

    assert plugin.get_tool("calculator") is tool
    assert tool.get_capabilities() == [
        "calculation",
    ]


def test_capability_registry_maps_plugin_tool():
    tool = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    plugin = Plugin(
        name="math_plugin",
        version="1.0",
        description="Math tools",
        tools=[
            tool,
        ],
    )

    capability_registry = CapabilityRegistry()

    capability_registry.register(
        Capability(
            name="calculation",
        )
    )

    matched_tools = (
        capability_registry.get_tools_for_capability(
            "calculation",
            plugin.get_tools(),
        )
    )

    assert matched_tools == [
        tool,
    ]


def test_tool_registry_registers_plugin_tools():
    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    search = AgentTool(
        name="search",
        capabilities=[
            "web_search",
        ],
    )

    plugin = Plugin(
        name="utility_plugin",
        version="1.0",
        description="Utility tools",
        tools=[
            calculator,
            search,
        ],
    )

    tool_registry = ToolRegistry()

    for tool in plugin.get_tools():
        assert tool_registry.register(
            tool
        ) is True

    assert tool_registry.count() == 2
    assert tool_registry.get(
        "calculator"
    ) is calculator
    assert tool_registry.get(
        "search"
    ) is search


def test_plugin_capability_and_tool_registry_work_together():
    calculator = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
            "arithmetic",
        ],
    )

    plugin = Plugin(
        name="math_plugin",
        version="1.0",
        description="Math tools",
        tools=[
            calculator,
        ],
    )

    capability_registry = CapabilityRegistry()

    capability_registry.register(
        Capability(
            name="calculation",
        )
    )

    tool_registry = ToolRegistry()

    for tool in plugin.get_tools():
        tool_registry.register(
            tool
        )

    matched_tools = (
        capability_registry.get_tools_for_capability(
            "calculation",
            tool_registry.list_tools(),
        )
    )

    assert matched_tools == [
        calculator,
    ]

    assert tool_registry.has(
        "calculator"
    ) is True


def test_extensibility_objects_remain_separate():
    tool = AgentTool(
        name="calculator",
        capabilities=[
            "calculation",
        ],
    )

    plugin = Plugin(
        name="math_plugin",
        version="1.0",
        description="Math tools",
        tools=[
            tool,
        ],
    )

    capability = Capability(
        name="calculation",
    )

    capability_registry = CapabilityRegistry()
    capability_registry.register(
        capability
    )

    tool_registry = ToolRegistry()
    tool_registry.register(
        tool
    )

    assert plugin.get_tool(
        "calculator"
    ) is tool

    assert capability_registry.get(
        "calculation"
    ) is capability

    assert tool_registry.get(
        "calculator"
    ) is tool

    assert capability_registry.get_tools_for_capability(
        "calculation",
        tool_registry.list_tools(),
    ) == [
        tool,
    ]