"""
Ultron Plugin Registry
Version: v0.92

Central registry for Plugin objects.

Responsibilities:
- Register plugins
- Unregister plugins
- Retrieve plugins
- Check plugin availability
- List registered plugins
- Clear registered plugins

PluginRegistry manages plugin definitions only.
Plugin execution belongs to AgentTool / AgentEngine layers.
"""

from typing import Dict, List, Optional

from modules.agent.plugin import Plugin


class PluginRegistryError(Exception):
    """Raised when a plugin registry operation fails."""


class PluginRegistry:
    """
    Central registry for Ultron Plugins.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    # ========================================================
    # Registration
    # ========================================================

    def register(
        self,
        plugin: Plugin,
    ) -> bool:
        """
        Register a plugin.

        Duplicate plugin names are rejected.
        """

        if not isinstance(
            plugin,
            Plugin,
        ):
            raise PluginRegistryError(
                "Only Plugin objects can be registered."
            )

        plugin.validate()

        if plugin.name in self._plugins:
            return False

        self._plugins[plugin.name] = plugin

        return True

    # ========================================================
    # Unregistration
    # ========================================================

    def unregister(
        self,
        plugin_name: str,
    ) -> bool:
        """
        Remove a plugin from the registry.
        """

        if not isinstance(
            plugin_name,
            str,
        ):
            raise PluginRegistryError(
                "Plugin name must be a string."
            )

        plugin_name = plugin_name.strip()

        if plugin_name not in self._plugins:
            return False

        del self._plugins[plugin_name]

        return True

    # ========================================================
    # Retrieval
    # ========================================================

    def get(
        self,
        plugin_name: str,
    ) -> Optional[Plugin]:
        """
        Retrieve a registered plugin by name.
        """

        if not isinstance(
            plugin_name,
            str,
        ):
            return None

        return self._plugins.get(
            plugin_name.strip()
        )

    # ========================================================
    # Availability
    # ========================================================

    def has(
        self,
        plugin_name: str,
    ) -> bool:
        """
        Check whether a plugin is registered.
        """

        if not isinstance(
            plugin_name,
            str,
        ):
            return False

        return (
            plugin_name.strip()
            in self._plugins
        )

    # ========================================================
    # Listing
    # ========================================================

    def list_plugins(
        self,
    ) -> List[Plugin]:
        """
        Return all registered plugins.
        """

        return list(
            self._plugins.values()
        )

    def list_plugin_names(
        self,
    ) -> List[str]:
        """
        Return the names of all registered plugins.
        """

        return list(
            self._plugins.keys()
        )

    # ========================================================
    # Registry Management
    # ========================================================

    def clear(self) -> None:
        """
        Remove all registered plugins.
        """

        self._plugins.clear()

    def count(self) -> int:
        """
        Return the number of registered plugins.
        """

        return len(
            self._plugins
        )

    # ========================================================
    # Representation
    # ========================================================

    def __len__(self) -> int:
        """
        Return the number of registered plugins.
        """

        return len(
            self._plugins
        )

    def __contains__(
        self,
        plugin_name: str,
    ) -> bool:
        """
        Support:

            "example_plugin" in registry
        """

        return self.has(
            plugin_name
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"PluginRegistry("
            f"plugins={self.list_plugin_names()}"
            f")"
        )