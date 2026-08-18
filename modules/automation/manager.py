"""
Ultron Automation Manager
Version: v0.34

Management layer for Ultron automations.
"""

from typing import Any, Dict, Optional

from modules.automation.engine import (
    AutomationEngine,
    AutomationValidationError,
)


class AutomationManager:
    """
    High-level manager for creating and managing automations.

    The manager delegates execution and validation to the
    AutomationEngine while providing a simpler interface
    for Ultron's command/conversation layers.
    """

    def __init__(
        self,
        engine: Optional[AutomationEngine] = None,
    ) -> None:

        self.engine = engine or AutomationEngine()

    # ========================================================
    # Action Management
    # ========================================================

    def register_action(
        self,
        action_name: str,
        handler,
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
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new automation.

        Returns:
            Automation ID.
        """

        return self.engine.register_automation(
            name=name,
            action=action,
            parameters=parameters,
        )

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

    def list_automations(self) -> list[Dict[str, Any]]:
        """
        Return all automations.
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
        Enable an automation.
        """

        return self.engine.enable_automation(
            automation_id
        )

    # ========================================================
    # Disable Automation
    # ========================================================

    def disable(
        self,
        automation_id: str,
    ) -> bool:
        """
        Disable an automation.
        """

        return self.engine.disable_automation(
            automation_id
        )

    # ========================================================
    # Run Automation
    # ========================================================

    def run(
        self,
        automation_id: str,
    ) -> Any:
        """
        Execute an automation.
        """

        return self.engine.execute(
            automation_id
        )

    # ========================================================
    # Delete Automation
    # ========================================================

    def delete(
        self,
        automation_id: str,
    ) -> bool:
        """
        Delete an automation.
        """

        return self.engine.delete_automation(
            automation_id
        )

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

        automation = self.get_automation(
            automation_id
        )

        if automation is None:
            return None

        if automation.get("enabled"):
            return "enabled"

        return "disabled"