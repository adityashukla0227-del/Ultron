"""
Ultron Tool Registry
Version: v0.38

Central registry for AgentTool objects.

Responsibilities:
- Register tools
- Unregister tools
- Retrieve tools
- Check tool availability
- List registered tools
- Filter enabled tools
- Execute registered tools
- Safely execute registered tools
"""


from typing import Any, Dict, List, Optional

from modules.agent.tool import AgentTool
from modules.agent.tool_result import ToolResult


class ToolRegistryError(Exception):
    """Raised when a tool registry operation fails."""


class ToolRegistry:
    """
    Central registry for Ultron AgentTools.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, AgentTool] = {}

    # ========================================================
    # Registration
    # ========================================================

    def register(
        self,
        tool: AgentTool,
    ) -> bool:
        """
        Register a tool.

        Duplicate tool names are rejected.
        """

        if not isinstance(
            tool,
            AgentTool,
        ):
            raise ToolRegistryError(
                "Only AgentTool objects can be registered."
            )

        tool.validate()

        if tool.name in self._tools:
            return False

        self._tools[tool.name] = tool

        return True

    # ========================================================
    # Unregistration
    # ========================================================

    def unregister(
        self,
        tool_name: str,
    ) -> bool:
        """
        Remove a tool from the registry.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            raise ToolRegistryError(
                "Tool name must be a string."
            )

        tool_name = tool_name.strip()

        if tool_name not in self._tools:
            return False

        del self._tools[tool_name]

        return True

    # ========================================================
    # Retrieval
    # ========================================================

    def get(
        self,
        tool_name: str,
    ) -> Optional[AgentTool]:
        """
        Retrieve a registered tool by name.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            return None

        return self._tools.get(
            tool_name.strip()
        )

    # ========================================================
    # Availability
    # ========================================================

    def has(
        self,
        tool_name: str,
    ) -> bool:
        """
        Check whether a tool is registered.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            return False

        return (
            tool_name.strip()
            in self._tools
        )

    # ========================================================
    # Listing
    # ========================================================

    def list_tools(
        self,
    ) -> List[AgentTool]:
        """
        Return all registered tools.
        """

        return list(
            self._tools.values()
        )

    def list_tool_names(
        self,
    ) -> List[str]:
        """
        Return the names of all registered tools.
        """

        return list(
            self._tools.keys()
        )

    # ========================================================
    # Enabled Tools
    # ========================================================

    def get_enabled_tools(
        self,
    ) -> List[AgentTool]:
        """
        Return only enabled registered tools.
        """

        return [
            tool
            for tool in self._tools.values()
            if tool.is_enabled()
        ]

    # ========================================================
    # Execution
    # ========================================================

    def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute a registered tool by name.

        Raises:
            ToolRegistryError:
                If the tool is not registered.

        Returns:
            ToolResult returned by the AgentTool.
        """

        tool = self.get(
            tool_name
        )

        if tool is None:
            raise ToolRegistryError(
                f"Tool '{tool_name}' is not registered."
            )

        return tool.execute(
            **kwargs
        )

    # ========================================================
    # Safe Execution
    # ========================================================

    def execute_safe(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Safely execute a registered tool.

        Unlike execute(), this method never exposes
        registry-level execution failures as raw exceptions.

        Every execution path returns a ToolResult.

        This provides a predictable interface for:

        - AgentEngine
        - API responses
        - Background workers
        - Workflow execution
        - Agent orchestration
        """

        tool = self.get(
            tool_name
        )

        if tool is None:

            return ToolResult(
                tool_name=(
                    tool_name
                    if isinstance(
                        tool_name,
                        str,
                    )
                    else str(tool_name)
                ),
                success=False,
                result=None,
                error=(
                    f"Tool '{tool_name}' "
                    f"is not registered."
                ),
            )

        try:

            result = tool.execute(
                **kwargs
            )

            if isinstance(
                result,
                ToolResult,
            ):
                return result

            return ToolResult(
                tool_name=tool.name,
                success=True,
                result=result,
                error=None,
            )

        except Exception as exc:

            return ToolResult(
                tool_name=tool.name,
                success=False,
                result=None,
                error=str(exc),
            )

    # ========================================================
    # Registry Management
    # ========================================================

    def clear(self) -> None:
        """
        Remove all registered tools.
        """

        self._tools.clear()

    def count(self) -> int:
        """
        Return the number of registered tools.
        """

        return len(
            self._tools
        )

    # ========================================================
    # Representation
    # ========================================================

    def __len__(self) -> int:
        """
        Return the number of registered tools.
        """

        return len(
            self._tools
        )

    def __contains__(
        self,
        tool_name: str,
    ) -> bool:
        """
        Support:

            "calculator" in registry
        """

        return self.has(
            tool_name
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"ToolRegistry("
            f"tools={self.list_tool_names()}"
            f")"
        )