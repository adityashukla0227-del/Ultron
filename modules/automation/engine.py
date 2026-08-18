"""
Ultron Automation Engine
Version: v0.36

Core engine for creating, registering, restoring, validating,
and executing automation tasks.
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional
import uuid

from modules.automation.actions import ActionRegistry


class AutomationError(Exception):
    """Base exception for automation errors."""


class AutomationValidationError(AutomationError):
    """Raised when an automation is invalid."""


class AutomationExecutionError(AutomationError):
    """Raised when an automation fails during execution."""


class AutomationEngine:
    """
    Central engine for Ultron's automation system.

    The engine provides:
    - Automation registration
    - Automation restoration
    - Automation validation
    - Centralized action registry
    - Automation execution
    - Execution result tracking
    - Automation enable/disable
    - Automation deletion
    """

    def __init__(
        self,
        action_registry: Optional[ActionRegistry] = None,
    ) -> None:

        self.automations: Dict[str, Dict[str, Any]] = {}

        self.action_registry = (
            action_registry
            or ActionRegistry()
        )

    # ========================================================
    # Action Registration
    # ========================================================

    def register_action(
        self,
        action_name: str,
        handler: Callable[..., Any],
    ) -> bool:
        """
        Register an executable automation action.
        """

        return self.action_registry.register(
            action_name,
            handler,
        )

    # ========================================================
    # Action Lookup
    # ========================================================

    def get_action(
        self,
        action_name: str,
    ) -> Optional[Callable[..., Any]]:
        """
        Return a registered action handler.
        """

        return self.action_registry.get(
            action_name
        )

    # ========================================================
    # List Actions
    # ========================================================

    def list_actions(self) -> list[str]:
        """
        Return all registered action names.
        """

        return self.action_registry.list_actions()

    # ========================================================
    # Automation Validation
    # ========================================================

    def validate_automation(
        self,
        automation: Dict[str, Any],
    ) -> bool:
        """
        Validate the basic automation structure.

        This validation is intended for new automation
        registration and therefore also verifies that the
        referenced action exists in the action registry.
        """

        if not isinstance(
            automation,
            dict,
        ):
            raise AutomationValidationError(
                "Automation must be a dictionary."
            )

        name = automation.get("name")
        action = automation.get("action")

        if not isinstance(
            name,
            str,
        ) or not name.strip():

            raise AutomationValidationError(
                "Automation name is required."
            )

        if not isinstance(
            action,
            str,
        ) or not action.strip():

            raise AutomationValidationError(
                "Automation action is required."
            )

        action = action.strip().lower()

        if not self.action_registry.exists(
            action
        ):
            raise AutomationValidationError(
                f"Unknown automation action: {action}"
            )

        parameters = automation.get(
            "parameters",
            {},
        )

        if not isinstance(
            parameters,
            dict,
        ):
            raise AutomationValidationError(
                "Automation parameters must be a dictionary."
            )

        return True

    # ========================================================
    # Automation Registration
    # ========================================================

    def register_automation(
        self,
        name: str,
        action: str,
        parameters: Optional[
            Dict[str, Any]
        ] = None,
    ) -> str:
        """
        Create and register a new automation.

        Returns:
            Unique automation ID.
        """

        automation = {
            "name": name,
            "action": action,
            "parameters": parameters or {},
        }

        self.validate_automation(
            automation
        )

        automation_id = str(
            uuid.uuid4()
        )

        self.automations[
            automation_id
        ] = {
            "id": automation_id,
            "name": name.strip(),
            "action": action.strip().lower(),
            "parameters": dict(
                parameters or {}
            ),
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "last_result": None,
        }

        return automation_id

    # ========================================================
    # Restore Automation
    # ========================================================

    def restore_automation(
        self,
        automation: Dict[str, Any],
    ) -> str:
        """
        Restore an existing automation from persistent storage.

        Runtime action handlers are intentionally NOT required
        during restoration.

        Action handlers are runtime objects and are expected to
        be registered again when the application starts.

        This allows persisted automations to be restored before
        their runtime handlers are registered.
        """

        if not isinstance(
            automation,
            dict,
        ):
            raise AutomationValidationError(
                "Automation must be a dictionary."
            )

        automation_id = automation.get(
            "id"
        )

        if not isinstance(
            automation_id,
            str,
        ) or not automation_id.strip():

            raise AutomationValidationError(
                "Automation ID is required."
            )

        name = automation.get(
            "name"
        )

        if not isinstance(
            name,
            str,
        ) or not name.strip():

            raise AutomationValidationError(
                "Automation name is required."
            )

        action = automation.get(
            "action"
        )

        if not isinstance(
            action,
            str,
        ) or not action.strip():

            raise AutomationValidationError(
                "Automation action is required."
            )

        parameters = automation.get(
            "parameters",
            {},
        )

        if not isinstance(
            parameters,
            dict,
        ):
            raise AutomationValidationError(
                "Automation parameters must be a dictionary."
            )

        enabled = automation.get(
            "enabled",
            True,
        )

        if not isinstance(
            enabled,
            bool,
        ):
            raise AutomationValidationError(
                "Automation enabled state must be boolean."
            )

        restored = {
            "id": automation_id,
            "name": name.strip(),
            "action": action.strip().lower(),
            "parameters": dict(
                parameters
            ),
            "enabled": enabled,
            "created_at": automation.get(
                "created_at",
                datetime.now().isoformat(),
            ),
            "last_run": automation.get(
                "last_run"
            ),
            "last_result": automation.get(
                "last_result"
            ),
        }

        self.automations[
            automation_id
        ] = restored

        return automation_id

    # ========================================================
    # Get Automation
    # ========================================================

    def get_automation(
        self,
        automation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return an automation by ID.
        """

        return self.automations.get(
            automation_id
        )

    # ========================================================
    # Enable Automation
    # ========================================================

    def enable_automation(
        self,
        automation_id: str,
    ) -> bool:
        """
        Enable an automation.
        """

        automation = self.get_automation(
            automation_id
        )

        if automation is None:
            return False

        automation["enabled"] = True

        return True

    # ========================================================
    # Disable Automation
    # ========================================================

    def disable_automation(
        self,
        automation_id: str,
    ) -> bool:
        """
        Disable an automation.
        """

        automation = self.get_automation(
            automation_id
        )

        if automation is None:
            return False

        automation["enabled"] = False

        return True

    # ========================================================
    # Execute Automation
    # ========================================================

    def execute(
        self,
        automation_id: str,
    ) -> Any:
        """
        Execute a registered automation.
        """

        automation = self.get_automation(
            automation_id
        )

        if automation is None:
            raise AutomationExecutionError(
                "Automation not found."
            )

        if not automation.get(
            "enabled",
            True,
        ):
            raise AutomationExecutionError(
                "Automation is disabled."
            )

        action_name = automation[
            "action"
        ]

        handler = self.get_action(
            action_name
        )

        if handler is None:
            raise AutomationExecutionError(
                f"Action handler not found: "
                f"{action_name}"
            )

        parameters = automation.get(
            "parameters",
            {},
        )

        try:

            result = handler(
                **parameters
            )

            automation["last_run"] = (
                datetime.now().isoformat()
            )

            automation["last_result"] = result

            return result

        except Exception as exc:

            automation["last_run"] = (
                datetime.now().isoformat()
            )

            automation["last_result"] = {
                "success": False,
                "error": str(exc),
            }

            raise AutomationExecutionError(
                f"Automation execution failed: "
                f"{exc}"
            ) from exc

    # ========================================================
    # List Automations
    # ========================================================

    def list_automations(
        self,
    ) -> list[Dict[str, Any]]:
        """
        Return all registered automations.
        """

        return list(
            self.automations.values()
        )

    # ========================================================
    # Delete Automation
    # ========================================================

    def delete_automation(
        self,
        automation_id: str,
    ) -> bool:
        """
        Delete an automation.
        """

        if automation_id not in self.automations:
            return False

        del self.automations[
            automation_id
        ]

        return True