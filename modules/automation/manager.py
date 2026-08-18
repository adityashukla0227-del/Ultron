"""
Ultron Automation Manager
Version: v0.35

Persistent management layer for Ultron automations.

Responsibilities:
- Create and manage automations
- Delegate execution to AutomationEngine
- Persist automations through AutomationStorage
- Restore saved automations when the manager starts
- Persist state changes
"""

from typing import Any, Callable, Dict, Optional

from modules.automation.engine import (
    AutomationEngine,
)
from modules.automation.storage import AutomationStorage


class AutomationManager:
    """
    High-level manager for creating and managing automations.

    The manager connects the AutomationEngine with the
    persistent AutomationStorage layer.
    """

    def __init__(
        self,
        engine: Optional[AutomationEngine] = None,
        storage: Optional[AutomationStorage] = None,
    ) -> None:

        self.engine = (
            engine
            or AutomationEngine()
        )

        self.storage = (
            storage
            or AutomationStorage()
        )

        self._restore_automations()

    # ========================================================
    # Storage
    # ========================================================

    def _restore_automations(self) -> None:
        """
        Restore persisted automations into the engine.

        Existing automations already registered in the engine
        are not duplicated.
        """

        stored_automations = (
            self.storage.list_automations()
        )

        for automation in stored_automations:

            automation_id = automation.get(
                "id"
            )

            if not automation_id:
                continue

            if self.engine.get_automation(
                automation_id
            ) is not None:
                continue

            try:

                self.engine.restore_automation(
                    automation
                )

            except Exception:
                # Ignore invalid persisted entries
                # instead of preventing the manager
                # from starting.
                continue

    def _persist_automation(
        self,
        automation_id: str,
    ) -> None:
        """
        Persist one automation using its
        current engine state.
        """

        automation = (
            self.engine.get_automation(
                automation_id
            )
        )

        if automation is None:
            return

        self.storage.save_automation(
            automation
        )

    # ========================================================
    # Action Management
    # ========================================================

    def register_action(
        self,
        action_name: str,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Register an action with the automation engine.
        """

        return self.engine.register_action(
            action_name,
            handler,
        )

    # ========================================================
    # Create Automation
    # ========================================================

    def create_automation(
        self,
        name: str,
        action: str,
        parameters: Optional[
            Dict[str, Any]
        ] = None,
    ) -> str:
        """
        Create and persist a new automation.

        Returns:
            Automation ID.
        """

        automation_id = (
            self.engine.register_automation(
                name=name,
                action=action,
                parameters=parameters,
            )
        )

        self._persist_automation(
            automation_id
        )

        return automation_id

    # ========================================================
    # Get Automation
    # ========================================================

    def get_automation(
        self,
        automation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get an automation by ID.
        """

        return self.engine.get_automation(
            automation_id
        )

    # ========================================================
    # List Automations
    # ========================================================

    def list_automations(
        self,
    ) -> list[Dict[str, Any]]:
        """
        Return all currently loaded automations.
        """

        return self.engine.list_automations()

    # ========================================================
    # Enable Automation
    # ========================================================

    def enable(
        self,
        automation_id: str,
    ) -> bool:
        """
        Enable an automation and persist the change.
        """

        result = (
            self.engine.enable_automation(
                automation_id
            )
        )

        if result:
            self._persist_automation(
                automation_id
            )

        return result

    # ========================================================
    # Disable Automation
    # ========================================================

    def disable(
        self,
        automation_id: str,
    ) -> bool:
        """
        Disable an automation and persist the change.
        """

        result = (
            self.engine.disable_automation(
                automation_id
            )
        )

        if result:
            self._persist_automation(
                automation_id
            )

        return result

    # ========================================================
    # Run Automation
    # ========================================================

    def run(
        self,
        automation_id: str,
    ) -> Any:
        """
        Execute an automation and persist its
        updated execution state.
        """

        result = self.engine.execute(
            automation_id
        )

        self._persist_automation(
            automation_id
        )

        return result

    # ========================================================
    # Delete Automation
    # ========================================================

    def delete(
        self,
        automation_id: str,
    ) -> bool:
        """
        Delete an automation from both the engine
        and persistent storage.
        """

        result = (
            self.engine.delete_automation(
                automation_id
            )
        )

        if result:
            self.storage.delete_automation(
                automation_id
            )

        return result

    # ========================================================
    # Automation Status
    # ========================================================

    def status(
        self,
        automation_id: str,
    ) -> Optional[str]:
        """
        Return the current automation status.
        """

        automation = (
            self.get_automation(
                automation_id
            )
        )

        if automation is None:
            return None

        if automation.get(
            "enabled"
        ):
            return "enabled"

        return "disabled"

    # ========================================================
    # Storage Access
    # ========================================================

    def save(self) -> None:
        """
        Persist all currently loaded automations.
        """

        for automation in (
            self.engine.list_automations()
        ):

            self.storage.save_automation(
                automation
            )

    def reload(self) -> None:
        """
        Reload persisted automations.

        Existing engine automations are preserved.
        """

        self._restore_automations()