"""
Ultron Automation Actions
Version: v0.34

Defines the action registry used by the automation system.
"""

from typing import Any, Callable, Dict


class ActionRegistry:
    """
    Registry for approved automation actions.

    Actions are explicitly registered before they can be
    executed by the Automation Engine.
    """

    def __init__(self) -> None:
        self._actions: Dict[str, Callable[..., Any]] = {}

    # ========================================================
    # Register Action
    # ========================================================

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Register a new automation action.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Action name must be a string."
            )

        name = name.strip().lower()

        if not name:
            raise ValueError(
                "Action name cannot be empty."
            )

        if not callable(handler):
            raise TypeError(
                "Action handler must be callable."
            )

        self._actions[name] = handler

        return True

    # ========================================================
    # Get Action
    # ========================================================

    def get(
        self,
        name: str,
    ) -> Callable[..., Any] | None:
        """
        Return a registered action.
        """

        if not isinstance(name, str):
            return None

        return self._actions.get(
            name.strip().lower()
        )

    # ========================================================
    # Has Action
    # ========================================================

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an action exists.
        """

        return self.get(name) is not None

    # ========================================================
    # Remove Action
    # ========================================================

    def remove(
        self,
        name: str,
    ) -> bool:
        """
        Remove a registered action.
        """

        name = name.strip().lower()

        if name not in self._actions:
            return False

        del self._actions[name]

        return True

    # ========================================================
    # List Actions
    # ========================================================

    def list_actions(self) -> list[str]:
        """
        Return all registered action names.
        """

        return sorted(
            self._actions.keys()
        )

    # ========================================================
    # Execute Action
    # ========================================================

    def execute(
        self,
        name: str,
        **parameters: Any,
    ) -> Any:
        """
        Execute a registered action.
        """

        handler = self.get(name)

        if handler is None:
            raise ValueError(
                f"Unknown automation action: {name}"
            )

        return handler(**parameters)


# ============================================================
# Default Safe Actions
# ============================================================

def create_default_action_registry() -> ActionRegistry:
    """
    Create an action registry with basic safe actions.

    External integrations will be added later.
    """

    registry = ActionRegistry()

    registry.register(
        "hello",
        lambda: "Hello from Ultron Automation!",
    )

    registry.register(
        "echo",
        lambda message="": message,
    )

    return registry