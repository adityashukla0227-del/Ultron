"""
Ultron Tool Selector
Version: v0.39

Provides deterministic tool selection for Ultron Agents.

Responsibilities:
- Inspect tools assigned to an agent
- Filter available/enabled tools
- Select tools by name
- Find candidate tools using descriptions
- Return standardized selection results

The selector does NOT execute tools.
Tool execution belongs to AgentEngine.
"""

from typing import List, Optional

from modules.agent.agent import Agent
from modules.agent.tool import AgentTool


class ToolSelectionError(Exception):
    """Raised when tool selection fails."""


class ToolSelector:
    """
    Deterministic selector for AgentTool objects.

    ToolSelector decides which tool should be used.
    It does not execute the selected tool.
    """

    def __init__(self) -> None:
        pass

    # ========================================================
    # Available Tools
    # ========================================================

    def get_available_tools(
        self,
        agent: Agent,
    ) -> List[AgentTool]:
        """
        Return enabled tools assigned to an agent.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise ToolSelectionError(
                "Only Agent instances can be inspected."
            )

        return [
            tool
            for tool in agent.get_tools()
            if tool.is_enabled()
        ]

    # ========================================================
    # Tool Names
    # ========================================================

    def get_available_tool_names(
        self,
        agent: Agent,
    ) -> List[str]:
        """
        Return names of enabled tools assigned to an agent.
        """

        return [
            tool.name
            for tool in self.get_available_tools(
                agent
            )
        ]

    # ========================================================
    # Exact Selection
    # ========================================================

    def select_by_name(
        self,
        agent: Agent,
        tool_name: str,
    ) -> Optional[AgentTool]:
        """
        Select an enabled tool by exact name.

        Returns:
            AgentTool if found, otherwise None.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            return None

        normalized_name = tool_name.strip()

        if not normalized_name:
            return None

        for tool in self.get_available_tools(
            agent
        ):
            if tool.name == normalized_name:
                return tool

        return None

    # ========================================================
    # Description Search
    # ========================================================

    def find_candidates(
        self,
        agent: Agent,
        query: str,
    ) -> List[AgentTool]:
        """
        Find enabled tools whose name or description
        contains the query text.

        Matching is case-insensitive.
        """

        if not isinstance(
            query,
            str,
        ):
            return []

        query = query.strip().lower()

        if not query:
            return []

        candidates = []

        for tool in self.get_available_tools(
            agent
        ):

            name = tool.name.lower()
            description = tool.description.lower()

            if (
                query in name
                or query in description
            ):
                candidates.append(
                    tool
                )

        return candidates

    # ========================================================
    # Automatic Selection
    # ========================================================

    def select(
        self,
        agent: Agent,
        query: str,
    ) -> Optional[AgentTool]:
        """
        Select a tool from a natural-language query.

        Selection priority:

        1. Exact tool name
        2. Single candidate from description/name search

        Returns:
            Selected AgentTool or None.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise ToolSelectionError(
                "Only Agent instances can be used."
            )

        if not isinstance(
            query,
            str,
        ):
            raise ToolSelectionError(
                "Tool selection query must be a string."
            )

        query = query.strip()

        if not query:
            return None

        exact = self.select_by_name(
            agent,
            query,
        )

        if exact is not None:
            return exact

        candidates = self.find_candidates(
            agent,
            query,
        )

        if len(candidates) == 1:
            return candidates[0]

        return None

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return "ToolSelector()"