"""
Ultron Capability Registry
Version: v0.93

Provides centralized registration and lookup for Ultron capabilities.

Responsibilities:
- Register capabilities
- Unregister capabilities
- Retrieve capabilities
- Check capability existence
- List registered capabilities
- Map capabilities to AgentTool objects

Capability definitions belong to Capability.
Capability registration belongs to CapabilityRegistry.
Capability authorization belongs to the security/permission layer.
Capability execution belongs to existing AgentTool / AgentEngine layers.
"""

from typing import Dict, List, Optional

from modules.agent.capability import (
    Capability,
)
from modules.agent.tool import AgentTool


class CapabilityRegistryError(Exception):
    """Raised when capability registry operations fail."""


class CapabilityRegistry:
    """
    Central registry for Ultron capabilities.

    The registry manages capability definitions only.
    It does not execute tools and does not grant permissions.
    """

    def __init__(
        self,
        capabilities: Optional[List[Capability]] = None,
    ) -> None:

        self._capabilities: Dict[str, Capability] = {}

        for capability in capabilities or []:
            self.register(capability)

    # ========================================================
    # Registration
    # ========================================================

    def register(
        self,
        capability: Capability,
    ) -> bool:
        """
        Register a capability.

        Duplicate capability names are ignored.
        """

        if not isinstance(
            capability,
            Capability,
        ):
            raise CapabilityRegistryError(
                "Capability must be a Capability object."
            )

        capability.validate()

        if capability.name in self._capabilities:
            return False

        self._capabilities[
            capability.name
        ] = capability

        return True

    def unregister(
        self,
        capability_name: str,
    ) -> bool:
        """
        Remove a capability by name.
        """

        if not isinstance(
            capability_name,
            str,
        ):
            raise CapabilityRegistryError(
                "Capability name must be a string."
            )

        capability_name = capability_name.strip()

        if capability_name not in self._capabilities:
            return False

        del self._capabilities[
            capability_name
        ]

        return True

    # ========================================================
    # Lookup
    # ========================================================

    def get(
        self,
        capability_name: str,
    ) -> Optional[Capability]:
        """
        Retrieve a capability by name.
        """

        if not isinstance(
            capability_name,
            str,
        ):
            return None

        capability_name = capability_name.strip()

        return self._capabilities.get(
            capability_name
        )

    def has(
        self,
        capability_name: str,
    ) -> bool:
        """
        Check whether a capability is registered.
        """

        if not isinstance(
            capability_name,
            str,
        ):
            return False

        capability_name = capability_name.strip()

        return capability_name in self._capabilities

    # ========================================================
    # Listing
    # ========================================================

    def list_capabilities(
        self,
    ) -> List[Capability]:
        """
        Return all registered capabilities.
        """

        return list(
            self._capabilities.values()
        )

    def list_capability_names(
        self,
    ) -> List[str]:
        """
        Return all registered capability names.
        """

        return list(
            self._capabilities.keys()
        )

    # ========================================================
    # Tool Mapping
    # ========================================================

    def get_tools_for_capability(
        self,
        capability_name: str,
        tools: List[AgentTool],
    ) -> List[AgentTool]:
        """
        Return tools that provide a capability.

        The registry does not own or mutate the tools.
        """

        if not isinstance(
            capability_name,
            str,
        ):
            raise CapabilityRegistryError(
                "Capability name must be a string."
            )

        if not isinstance(
            tools,
            list,
        ):
            raise CapabilityRegistryError(
                "Tools must be provided as a list."
            )

        capability_name = capability_name.strip()

        if not capability_name:
            raise CapabilityRegistryError(
                "Capability name is required."
            )

        matched_tools: List[AgentTool] = []

        for tool in tools:
            if not isinstance(
                tool,
                AgentTool,
            ):
                raise CapabilityRegistryError(
                    "Tools must contain AgentTool objects."
                )

            if capability_name in tool.get_capabilities():
                matched_tools.append(tool)

        return matched_tools

    # ========================================================
    # Registry Management
    # ========================================================

    def clear(self) -> None:
        """
        Remove all registered capabilities.
        """

        self._capabilities.clear()

    def count(self) -> int:
        """
        Return the number of registered capabilities.
        """

        return len(
            self._capabilities
        )

    def __len__(self) -> int:
        """
        Return the number of registered capabilities.
        """

        return self.count()

    def __contains__(
        self,
        capability_name: str,
    ) -> bool:
        """
        Support membership checks.
        """

        return self.has(
            capability_name
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"CapabilityRegistry("
            f"capabilities="
            f"{self.list_capability_names()}"
            f")"
        )