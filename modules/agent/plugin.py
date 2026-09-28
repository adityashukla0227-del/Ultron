"""
Ultron Plugin
Version: v0.92

Defines the core plugin contract for Ultron.

Responsibilities:
- Define plugin identity
- Store plugin version
- Store plugin description
- Store plugin metadata
- Store plugin-provided AgentTool objects
- Validate plugin configuration

Plugin management belongs to PluginRegistry.
Plugin execution belongs to existing AgentTool / AgentEngine layers.
"""

from typing import Any, Dict, List, Optional

from modules.agent.tool import AgentTool


class PluginValidationError(Exception):
    """Raised when a plugin configuration is invalid."""


class Plugin:
    """
    Core representation of an Ultron plugin.

    A Plugin describes an extension and the AgentTools
    provided by that extension.

    Plugin does not execute tools.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0",
        description: str = "",
        tools: Optional[List[AgentTool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.name = (
            name.strip()
            if isinstance(name, str)
            else name
        )

        self.version = (
            version.strip()
            if isinstance(version, str)
            else version
        )

        self.description = (
            description.strip()
            if isinstance(description, str)
            else description
        )

        self.tools: List[AgentTool] = []

        for tool in tools or []:
            if not isinstance(tool, AgentTool):
                raise PluginValidationError(
                    "Plugin tools must contain AgentTool objects."
                )

            self.tools.append(tool)

        if metadata is None:
            self.metadata = {}
        elif isinstance(metadata, dict):
            self.metadata = dict(metadata)
        else:
            raise PluginValidationError(
                "Plugin metadata must be a dictionary."
            )

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete plugin configuration.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise PluginValidationError(
                "Plugin name must be a string."
            )

        if not self.name.strip():
            raise PluginValidationError(
                "Plugin name is required."
            )

        if not isinstance(
            self.version,
            str,
        ):
            raise PluginValidationError(
                "Plugin version must be a string."
            )

        if not self.version.strip():
            raise PluginValidationError(
                "Plugin version is required."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise PluginValidationError(
                "Plugin description must be a string."
            )

        if not isinstance(
            self.tools,
            list,
        ):
            raise PluginValidationError(
                "Plugin tools must be a list."
            )

        for tool in self.tools:
            if not isinstance(
                tool,
                AgentTool,
            ):
                raise PluginValidationError(
                    "Plugin tools must contain AgentTool objects."
                )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise PluginValidationError(
                "Plugin metadata must be a dictionary."
            )

        return True

    # ========================================================
    # Tool Management
    # ========================================================

    def add_tool(
        self,
        tool: AgentTool,
    ) -> bool:
        """
        Add an AgentTool provided by the plugin.

        Duplicate tool names are ignored.
        """

        if not isinstance(
            tool,
            AgentTool,
        ):
            raise PluginValidationError(
                "Plugin tool must be an AgentTool object."
            )

        if self.get_tool(
            tool.name
        ) is not None:
            return False

        self.tools.append(tool)

        return True

    def remove_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Remove a plugin-provided tool by name.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            raise PluginValidationError(
                "Tool name must be a string."
            )

        tool_name = tool_name.strip()

        tool = self.get_tool(
            tool_name
        )

        if tool is None:
            return False

        self.tools.remove(tool)

        return True

    def get_tool(
        self,
        tool_name: str,
    ) -> Optional[AgentTool]:
        """
        Retrieve a plugin-provided tool by name.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            return None

        tool_name = tool_name.strip()

        for tool in self.tools:
            if tool.name == tool_name:
                return tool

        return None

    def get_tools(
        self,
    ) -> List[AgentTool]:
        """
        Return all tools provided by the plugin.
        """

        return list(self.tools)

    # ========================================================
    # Metadata Management
    # ========================================================

    def set_metadata(
        self,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        """
        Replace plugin metadata.
        """

        if metadata is None:
            metadata = {}

        if not isinstance(
            metadata,
            dict,
        ):
            raise PluginValidationError(
                "Plugin metadata must be a dictionary."
            )

        self.metadata = dict(metadata)

    def update_metadata(
        self,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Update plugin metadata.
        """

        if not isinstance(
            metadata,
            dict,
        ):
            raise PluginValidationError(
                "Plugin metadata must be a dictionary."
            )

        self.metadata.update(metadata)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return a defensive copy of plugin metadata.
        """

        return dict(self.metadata)

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert plugin configuration into a dictionary.
        """

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": [
                tool.to_dict()
                for tool in self.tools
            ],
            "metadata": dict(
                self.metadata
            ),
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Plugin":
        """
        Restore a Plugin from persistent data.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise PluginValidationError(
                "Plugin data must be a dictionary."
            )

        tools_data = data.get(
            "tools",
            [],
        )

        if not isinstance(
            tools_data,
            list,
        ):
            raise PluginValidationError(
                "Plugin tools data must be a list."
            )

        restored_tools = []

        for tool in tools_data:
            if not isinstance(
                tool,
                dict,
            ):
                raise PluginValidationError(
                    "Invalid tool data in plugin configuration."
                )

            restored_tools.append(
                AgentTool.from_dict(tool)
            )

        return cls(
            name=data.get(
                "name",
                "",
            ),
            version=data.get(
                "version",
                "1.0",
            ),
            description=data.get(
                "description",
                "",
            ),
            tools=restored_tools,
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"Plugin("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"tools={[tool.name for tool in self.tools]}"
            f")"
        )